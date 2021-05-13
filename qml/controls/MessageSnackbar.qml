import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15
import QtQuick.Layouts 1.11
import "../colors.js" as Colors
import "../controls"

Popup{
    id: root
    width: 400
    height: 50
    closePolicy: Popup.CloseOnEscape
    transformOrigin: Popup.Right
    x: parent.width - width - 30
    y: parent.height - 100

    property int    timer        : 3000
    property string message      : ''
    property string type         : 'success'
    property color  dynamicColor : if (type === 'warn') {
                                        '#dba100'
                                    } else if (type === 'error'){
                                        '#FF5252'               
                                    } else if (type === 'success'){
                                        '#4CAF50'
                                    }
        
    background: Rectangle{
        id: bg
        anchors.fill: parent
        color: dynamicColor
        smooth: true
        clip: true
        radius: 2

        Rectangle{
            id: progressBar
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            color: '#fff'
            radius: 20
            height: 2
            width: 0
            x: 0

            PropertyAnimation { 
                id: progressBarAnimation
                target: progressBar
                property: "width"
                to: bg.width
                duration: root.timer
            }
        }
    }

    contentItem: RowLayout{
        anchors.centerIn: parent
        Text{
            Layout.fillWidth: true
            text: root.message
            color: '#fff'
            font.pointSize: 11
            wrapMode: Text.Wrap
        }
        TextButton{
            primaryColor: root.dynamicColor
            hoverColor: root.dynamicColor
            clickColor: root.dynamicColor
            textColor: '#fff'
            texto: 'Fechar'
            textSize: 19
            onClicked: root.close()
        }
    }

    Timer {
        id: popupClose
        interval: root.timer
        onTriggered: root.close()
    }

    exit: Transition {
        NumberAnimation { property: "opacity"; from: 1.0; to: 0.0; duration: 200 }
    }
    enter: Transition {
        NumberAnimation { property: "opacity"; from: 0.0; to: 1.0; duration: 200 }
    }
    onOpened: {
        popupClose.running = true
        progressBarAnimation.running= true
    }
}