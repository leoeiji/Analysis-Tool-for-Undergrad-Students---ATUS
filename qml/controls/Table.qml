import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.11
import QtQuick.Dialogs 1.3
import "../colors.js" as Colors

Item{
    id: root
    // Public Variables
    property variant headerModel: []
    property variant headerKeys: headerModel.map(({text, width}) => text)
    property variant dataModel: []
    function addRow(rowObject) {
        dataSet.insert(dataSet.count, rowObject)
    }
    function clear(){
        dataSet.clear()
    }

    // Private
    width: 300
    height: 200

    // Header
    Rectangle{
        id: header
        width: parent.width
        height: 30
        color: Colors.color2
        radius: 0.03 * root.width

        // Half bottom of the header must be flat
        Rectangle{
            width: parent.width
            height: 0.5 * parent.height
            color: parent.color
            anchors.bottom: parent.bottom
        }

        ListView{
            anchors.fill: parent
            orientation: ListView.Horizontal
            interactive: false

            model: headerModel

            delegate: Item{
                // Header cell
                width: modelData.width * root.width
                height: header.height

                Text {
                    x: root.width
                    text: modelData.text
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pixelSize: 14
                    font.bold: true
                    color: 'white'
                }
            }
        }
    }

    Rectangle{
        id: table_bg
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: header.bottom
        anchors.bottom: footer.top
        anchors.topMargin: 0
        anchors.bottomMargin: 0
        color: Colors.color1

        ScrollView{
            anchors.fill: parent
            clip: true
            
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            ScrollBar.vertical.policy: ScrollBar.AsNeeded

            ListView{
                id: dataTable
                anchors.fill: parent
                clip: true
                interactive: true

                model: dataModel
                delegate: Item{
                    width: root.width
                    height: header.height

                    property int row: index
                    property variant dataRow:   if(dataModel.get(row) == undefined){
                                                    []
                                                }else{
                                                    Object.values(dataModel.get(row))
                                                }
                    

                    Row{
                        anchors.fill: parent
                        Repeater{
                            model: Object.keys(headerKeys)

                            delegate: Rectangle{
                                width: headerModel[index].width * parent.width
                                height: header.height
                                radius: 10
                                color: 'transparent'
                                TextEdit{
                                    anchors.fill: parent
                                    horizontalAlignment: TextEdit.AlignHCenter
                                    verticalAlignment: TextEdit.AlignVCenter
                                    readOnly: true
                                    selectByMouse: true
                                    font.pixelSize: 15
                                    color: 'white'
                                    clip: true

                                    text:   if(dataModel.get(row) == undefined){
                                                ''
                                            }else{
                                                if(typeof dataRow[index] == 'number'){
                                                    dataRow[index].toPrecision(5)
                                                }else{
                                                    dataRow[index]
                                                }
                                            }
                                }
                            }
                        }
                    }
                }
            }
        }

    }

    Rectangle{
        id: footer
        width: root.width
        height: 30
        color: Colors.color2
        radius: 0.03 * root.width

        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0

        Rectangle{
            width: parent.width
            height: parent.height/2
            color: parent.color
            
            anchors.top: parent.top
            anchors.topMargin: 0
        }
    }
}