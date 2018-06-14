import QtQuick 2.0
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.2

ApplicationWindow {
    visible: true
    width: 1024
    height: 768
    title: qsTr("Web2ChordPro")
    color: "whitesmoke"

    Frame {
        id: urlFrame
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right

        RowLayout {
            anchors.fill: parent

            Text {
                text: qsTr("URL: ")
            }

            TextField {
                objectName: "url"
                Layout.fillWidth: true
            }

            Button {
                objectName: "loadUrlButton"
                text: qsTr("Go!")
            }
        }
    }

    Frame {
        id: contentFrame
        anchors.top: urlFrame.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        Text {
            id: errorMsg
            objectName: "errorMsg"
            color: "red"
            visible: text.length > 0
            anchors.top: parent.top
        }

        TextField {
            id: songTitle
            objectName: "songTitle"
            font.pointSize: 16
            horizontalAlignment: TextEdit.AlignHCenter
            width: parent.width
            anchors.top: errorMsg.top
            anchors.left: parent.left
            anchors.right: parent.right
        }

        Row {
            id: row
            anchors.topMargin: 10
            anchors.top: songTitle.bottom
            anchors.left: parent.left
            anchors.right: parent.right

            Text {
                text: "Key: "
                height: parent.height
                verticalAlignment: "AlignVCenter"
            }

            TextField {
                objectName: "songKey"
            }
        }
    }
}
