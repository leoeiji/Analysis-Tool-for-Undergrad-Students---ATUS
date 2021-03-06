# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2021 Leonardo Eiji Tamayose, Guilherme Ferrari Fortino

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from PyQt5.QtCore import QObject, QJsonValue, QUrl, pyqtSignal, pyqtSlot
import pandas as pd
import numpy as np
import platform
import json

class Histogram(QObject):
    """Backend for histogram page"""

    # Signals
    fillPage = pyqtSignal(QJsonValue)

    def __init__(self, canvas, messageHandler) -> None:
        super().__init__()
        self.messageHandler = messageHandler
        self.canvas         = canvas
        self.path           = ""
        self.histAlign      = {"Centro" : "mid", "Direita" : "right", "Esquerda" : "left"}
        self.histOrient     = {"Vertical" : "vertical", "Horizontal" : "horizontal"}


########################### EDITE AQUI \/ #############################
    @pyqtSlot(QJsonValue)
    def plot(self, data):
        data = QJsonValue.toVariant(data)
        self.canvas.reset()
        if data["props"]["grid"]:
            self.canvas.axes.grid(True, which='major')
        if data["props"]["logy"]:
            self.canvas.axes.set_yscale('log')
        if data["props"]["logx"]:
            self.canvas.axes.set_xscale('log')

        xdiv = self.makeInt(data["props"]["xdiv"], 0.)
        xmin = self.makeFloat(data["props"]["xmin"], 0.)
        xmax = self.makeFloat(data["props"]["xmax"], 0.)
        ydiv = self.makeInt(data["props"]["ydiv"], 0.)
        ymin = self.makeFloat(data["props"]["ymin"], 0.)
        ymax = self.makeFloat(data["props"]["ymax"], 0.)

        if xdiv != 0. and (xmax != 0. or xmin != 0.):
            self.canvas.axes.set_xticks(np.linspace(xmin, xmax, xdiv + 1))
            self.canvas.axes.set_xlim(left = xmin, right = xmax)
        else:
            if xmin == 0. and xmax != 0.:
                self.canvas.axes.set_xlim(left = None, right = xmax)
            elif xmin != 0. and xmax == 0.:
                self.canvas.axes.set_xlim(left = xmin, right = None)
            elif xmin != 0. and xmax != 0.:
                self.canvas.axes.set_xlim(left = xmin, right = xmax)
        if ydiv != 0. and (ymax != 0. or ymin != 0.):
            self.canvas.axes.set_yticks(np.linspace(ymin, ymax, ydiv + 1))
            self.canvas.axes.set_ylim(bottom = ymin, top = ymax)
        else:
            if ymin == 0. and ymax != 0.:
                self.canvas.axes.set_ylim(bottom = None, top = ymax)
            elif ymin != 0. and ymax == 0.:
                self.canvas.axes.set_ylim(bottom = ymin, top = None)
            elif ymin != 0. and ymax != 0.:
                self.canvas.axes.set_ylim(bottom = ymin, top = ymax)
        has_legend = False
        for arquivo in data["data"]:
            if arquivo["visible"]:
                df    = pd.DataFrame.from_dict(json.loads(arquivo["data"]))
                alpha = self.makeFloat(arquivo["kargs"].pop("alpha"), 1.0)
                label = arquivo["kargs"].pop("label")
                left  = self.makeFloat(data["props"]["rangexmin"], np.floor(df["x"].min()))
                right = self.makeFloat(data["props"]["rangexmax"], np.ceil(df["x"].max()))
                if left >= right:
                    self.msg.raiseError("Intervalo de bins inválido. Rever intervalo de bins.")
                    return None
                bins  = np.linspace(left, right,
                 self.makeInt(data["props"]["nbins"], 10) + 1)
                counts = None
                if arquivo["legend"] == "":
                    counts, bins, _ = self.canvas.axes.hist(x = df["x"], bins = bins,
                    density     = data["props"]["norm"], cumulative = False, bottom = 0,
                    histtype    = data["props"]["histType"],
                    align       = self.histAlign[data["props"]["histAlign"]],
                    orientation = self.histOrient[data["props"]["histOrientation"]],
                    log = False, rwidth = 1, capstyle = "round", ls = "-", aa = True,
                    alpha = alpha,
                    **arquivo["kargs"])
                else:
                    counts, bins, _ = self.canvas.axes.hist(x = df["x"], bins = bins,
                    density     = data["props"]["norm"], cumulative = False, bottom = 0,
                    histtype    = data["props"]["histType"],
                    align       = self.histAlign[data["props"]["histAlign"]],
                    orientation = self.histOrient[data["props"]["histOrientation"]],
                    log = False, rwidth = 1, capstyle = "round", ls = "-", aa = True,
                    alpha = alpha, label = arquivo["legend"],
                    **arquivo["kargs"])
                    has_legend = True
                if label:
                    bottom, top = self.canvas.axes.get_ylim()
                    height = top - bottom
                    c = (bins[1] - bins[0])/2
                    for n, b in zip(counts, bins):
                        if n != 0:
                            self.canvas.axes.text(b + c, n + height*0.02, str(n), ha = "center")
        self.canvas.axes.set_title(data["props"]["title"])
        self.canvas.axes.set(xlabel = data["props"]["xaxis"], ylabel = data["props"]["yaxis"])
        if has_legend:
            self.canvas.axes.legend()
        self.canvas.figure.tight_layout()
        self.canvas.canvas.draw_idle()
########################### EDITE AQUI /\ #############################

    @pyqtSlot()
    def new(self):
        self.path = ""
        self.fillPage.emit(None)
        self.canvas.reset()

    @pyqtSlot(QJsonValue, result=bool)
    def save(self, data):
        # If there's no path for saving, saveAs()
        if self.path == '':
            return False

        # Getting properties
        data = data.toVariant()

        if platform.system() == "Linux":
            if self.path[-5:] == ".json":
                with open(self.path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
            else: 
                with open(self.path + ".json", 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
        else:
            with open(self.path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

        return True

    @pyqtSlot(str, QJsonValue)
    def saveAs(self, path, data):
        # Getting path
        self.path = QUrl(path).toLocalFile()
        self.save(data)

    @pyqtSlot(str)
    def load(self, path):
        # Reseting frontend
        self.new()

        # Getting path
        self.path = QUrl(path).toLocalFile()

        # Getting props
        with open(self.path, encoding='utf-8') as file:
            props = json.load(file)

        if "key" in props:
            if props["key"].split('-')[-1] != 'hist':
                self.messageHandler.raiseError("Este projeto pertence à outra aba do ATUS.")
                return 0
        else:
            self.messageHandler.raiseError("O arquivo carregado é incompatível com o ATUS.")
            return 0

        self.fillPage.emit(QJsonValue.fromVariant(props))

    @pyqtSlot(str, result=QJsonValue)
    def checkData(self, filePath):
        '''
        Check if data is valid
        Returns: True + Data if valid data, False otherwise
        '''
        package = {
            "isValid": False,
            "data"   : None
        }
        # Loading from .csv or (.txt and .tsv)
        filePath = QUrl(filePath).toLocalFile()
        if filePath[-3:] == "csv":
            try:
                df = pd.read_csv(filePath, sep=',', header=None, dtype = str).replace(np.nan, "0")
            except pd.errors.ParserError:
                self.messageHandler.raiseError("Separação de colunas de arquivos csv são com vírgula (","). Rever dados de entrada.")
                # Separação de colunas de arquivos csv são com vírgula (","). Rever dados de entrada.
                return QJsonValue.fromVariant(package)
        elif filePath[-3:] == "tsv" or filePath[-3:] == "txt":
            try:
                df = pd.read_csv(filePath, sep='\t', header=None, dtype = str).replace(np.nan, "0")
            except pd.errors.ParserError:
                self.messageHandler.raiseError("Separação de colunas de arquivos txt e tsv são com tab. Rever dados de entrada.")
                # Separação de colunas de arquivos txt e tsv são com tab. Rever dados de entrada.
                return QJsonValue.fromVariant(package)
        else:
            self.messageHandler.raiseError("Apenas arquivos .txt, .csv, .tsv são suportados.")
            return QJsonValue.fromVariant(package)

        if len(df.columns) == 1:
            df.columns = ["x"]
        else:
            self.messageHandler.raiseError("A tabela de histogramas deve conter no máximo 1 coluna.")
            return QJsonValue.fromVariant(package)
        
        for i in df.columns:
            # Replacing comma for dots
            df[i] = [x.replace(',', '.') for x in df[i]]
            # Converting everything to float
            try:
                df[i] = df[i].astype(float)
            except:
                self.messageHandler.raiseError("A entrada de dados só permite entrada de números. Rever arquivo de entrada.")
                # Há células não numéricas. A entrada de dados só permite entrada de números. Rever arquivo de entrada.
                return QJsonValue.fromVariant(package)

        package["data"] = df.to_json()
        package["isValid"] = True
        return package

    def makeFloat(self, var, value):
        try:
            return float(var)
        except:
            return value

    def makeInt(self, var, value):
        try:
            return int(var)
        except:
            return value