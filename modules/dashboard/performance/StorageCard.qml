import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Caelestia.Config
import Caelestia.I18n
import Caelestia.Services
import qs.components
import qs.components.controls
import qs.services
import qs.utils

StyledRect {
    id: root
    property var customDisks: []
    property var activeDisk: null
    property string _lsblkOutput: ""

    Process {
        id: lsblkProc
        command: ["lsblk", "-J", "-b", "-o", "NAME,LABEL,MOUNTPOINTS,SIZE,FSUSED"]
        running: true
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    const json = JSON.parse(text);
                    const disks = [];
                    function processBlockDevices(devices) {
                        for (let dev of (devices || [])) {
                            let mntArray = dev.mountpoints || [];
                            if (mntArray.includes("/boot") || mntArray.includes("[SWAP]")) {
                                continue; // ignore boot and swap
                            }
                            
                            let mnt = null;
                            if (mntArray.includes("/")) {
                                mnt = "/";
                            } else if (mntArray.length > 0) {
                                mnt = mntArray[0];
                            }
                            
                            if (mnt) {
                                const total = Math.floor((dev.size || 0) / 1024);
                                const used = Math.floor((dev.fsused || 0) / 1024);
                                const perc = total > 0 ? used / total : 0;
                                const hasRoot = (mnt === "/");
                                let name = dev.label || mnt;
                                if (name === "/") name = "File System";
                                disks.push({
                                    mount: mnt,
                                    label: name,
                                    used: used,
                                    total: total,
                                    free: total - used,
                                    perc: perc,
                                    hasRoot: hasRoot
                                });
                            }
                            if (dev.children) {
                                processBlockDevices(dev.children);
                            }
                        }
                    }
                    processBlockDevices(json.blockdevices);
                    disks.sort((a, b) => (b.hasRoot ? 1 : 0) - (a.hasRoot ? 1 : 0) || a.label.localeCompare(b.label));
                    
                    const oldActive = root.activeDisk;
                    root.customDisks = disks;
                    
                    if (oldActive) {
                        const match = disks.find(d => d.mount === oldActive.mount);
                        if (match) {
                            root.activeDisk = match;
                        } else {
                            root.activeDisk = disks.find(d => d.hasRoot) || disks[0];
                        }
                    } else if (disks.length > 0) {
                        root.activeDisk = disks.find(d => d.hasRoot) || disks[0];
                    }
                } catch (e) {
                    console.log("lsblk parse error: " + e);
                }
            }
        }
    }

    Timer {
        interval: 10000
        running: true
        repeat: true
        onTriggered: lsblkProc.running = true
    }

    readonly property color accent: Colours.palette.m3secondary
    readonly property real percentage: activeDisk?.perc ?? 0

    color: Colours.tPalette.m3surfaceContainer
    radius: Tokens.rounding.extraExtraLarge

    implicitWidth: layout.implicitWidth + layout.anchors.margins * 2
    implicitHeight: layout.implicitHeight + Tokens.padding.large * 2

    ColumnLayout {
        id: layout

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.margins: Tokens.padding.extraLarge
        spacing: 0

        RowLayout {
            id: row

            Layout.alignment: Qt.AlignHCenter
            spacing: Tokens.spacing.large

            CircularProgress {
                fgColour: root.accent
                value: root.percentage
                implicitSize: usageColumn.implicitHeight + thickness + Tokens.padding.large * 2
                startAngle: -225
                sweepAngle: 270

                Behavior on clampedVal {
                    Anim {}
                }

                ColumnLayout {
                    id: usageColumn

                    anchors.centerIn: parent
                    spacing: 0

                    MaterialIcon {
                        Layout.alignment: Qt.AlignHCenter
                        text: "hard_drive"
                        color: root.accent
                        fontStyle: Tokens.font.icon.medium
                    }

                    StyledText {
                        Layout.alignment: Qt.AlignHCenter
                        text: Strings.percentOne(root.percentage)
                        font: Tokens.font.title.builders.large.width(90).build()
                        color: root.accent
                    }

                    StyledText {
                        Layout.alignment: Qt.AlignHCenter
                        text: Tr.trCtx("Used", "storage used")
                        font: Tokens.font.body.small
                        color: Colours.palette.m3onSurfaceVariant
                    }
                }
            }

            ColumnLayout {
                Layout.minimumWidth: Tokens.sizes.dashboard.perfStorageTextWidth
                spacing: Tokens.spacing.extraSmall

                StyledText {
                    text: Tr.tr("Storage")
                    font: Tokens.font.title.medium
                }

                StyledText {
                    text: Storage.primaryDisk ? Units.formatKibUsage(Storage.primaryDisk.used, Storage.primaryDisk.total) : Tr.tr("No disks detected")
                    font: Tokens.font.body.large
                    color: root.accent
                }
            }
        }

        SplitButton {
            Layout.alignment: Qt.AlignHCenter
            Layout.minimumWidth: Math.max(row.implicitWidth * 0.6, implicitWidth)

            type: SplitButton.Tonal
            disabled: !root.customDisks.length
            fallbackIcon: "storage"
            fallbackText: Tr.tr("No disks")
            menuOnTop: true

            menuItems: disks.instances
            active: menuItems.find(m => m.modelData === root.activeDisk) ?? menuItems[0] ?? null
            menu.onItemSelected: item => root.activeDisk = (item as DiskItem).modelData

            Variants {
                id: disks

                model: root.customDisks

                DiskItem {}
            }
        }
    }

    component DiskItem: MenuItem {
        required property var modelData

        icon: modelData === root.activeDisk ? "check" : ""
        text: modelData.label
        activeIcon: "storage"
    }
}
