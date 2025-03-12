# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Tender.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QListView, QMainWindow,
    QMenuBar, QProgressBar, QPushButton, QSizePolicy,
    QStackedWidget, QStatusBar, QTableView, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1233, 801)
        self.NavMenu = QWidget(MainWindow)
        self.NavMenu.setObjectName(u"NavMenu")
        self.Nav_Menu_Container = QFrame(self.NavMenu)
        self.Nav_Menu_Container.setObjectName(u"Nav_Menu_Container")
        self.Nav_Menu_Container.setGeometry(QRect(10, 30, 158, 104))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Nav_Menu_Container.sizePolicy().hasHeightForWidth())
        self.Nav_Menu_Container.setSizePolicy(sizePolicy)
        self.Nav_Menu_Container.setFrameShape(QFrame.Shape.StyledPanel)
        self.Nav_Menu_Container.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.Nav_Menu_Container)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.Tender_Button = QPushButton(self.Nav_Menu_Container)
        self.Tender_Button.setObjectName(u"Tender_Button")

        self.verticalLayout.addWidget(self.Tender_Button)

        self.AI_Analysis_Button = QPushButton(self.Nav_Menu_Container)
        self.AI_Analysis_Button.setObjectName(u"AI_Analysis_Button")

        self.verticalLayout.addWidget(self.AI_Analysis_Button)

        self.pushButton_3 = QPushButton(self.Nav_Menu_Container)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.verticalLayout.addWidget(self.pushButton_3)

        self.PagePicker = QStackedWidget(self.NavMenu)
        self.PagePicker.setObjectName(u"PagePicker")
        self.PagePicker.setGeometry(QRect(180, 10, 1031, 641))
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.TenderList = QTableView(self.page)
        self.TenderList.setObjectName(u"TenderList")
        self.TenderList.setGeometry(QRect(20, 30, 711, 561))
        self.TenderDetails = QGroupBox(self.page)
        self.TenderDetails.setObjectName(u"TenderDetails")
        self.TenderDetails.setGeometry(QRect(740, 20, 282, 581))
        self.TenderName = QLabel(self.TenderDetails)
        self.TenderName.setObjectName(u"TenderName")
        self.TenderName.setGeometry(QRect(10, 26, 71, 16))
        self.TenderExpandedInfo = QTextEdit(self.TenderDetails)
        self.TenderExpandedInfo.setObjectName(u"TenderExpandedInfo")
        self.TenderExpandedInfo.setGeometry(QRect(10, 50, 261, 521))
        self.layoutWidget = QWidget(self.page)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(20, 600, 258, 26))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.ScrapeTendersButton = QPushButton(self.layoutWidget)
        self.ScrapeTendersButton.setObjectName(u"ScrapeTendersButton")

        self.horizontalLayout.addWidget(self.ScrapeTendersButton)

        self.ExportToPDFButton = QPushButton(self.layoutWidget)
        self.ExportToPDFButton.setObjectName(u"ExportToPDFButton")

        self.horizontalLayout.addWidget(self.ExportToPDFButton)

        self.AddTenderButton = QPushButton(self.layoutWidget)
        self.AddTenderButton.setObjectName(u"AddTenderButton")

        self.horizontalLayout.addWidget(self.AddTenderButton)

        self.PagePicker.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.DragAndDropFiles = QFrame(self.page_2)
        self.DragAndDropFiles.setObjectName(u"DragAndDropFiles")
        self.DragAndDropFiles.setGeometry(QRect(10, 190, 211, 80))
        self.DragAndDropFiles.setFrameShape(QFrame.Shape.StyledPanel)
        self.DragAndDropFiles.setFrameShadow(QFrame.Shadow.Raised)
        self.UploadFileButton = QPushButton(self.page_2)
        self.UploadFileButton.setObjectName(u"UploadFileButton")
        self.UploadFileButton.setGeometry(QRect(10, 280, 75, 24))
        self.FileList = QListView(self.page_2)
        self.FileList.setObjectName(u"FileList")
        self.FileList.setGeometry(QRect(10, 20, 211, 161))
        self.ProcessProgress = QProgressBar(self.page_2)
        self.ProcessProgress.setObjectName(u"ProcessProgress")
        self.ProcessProgress.setGeometry(QRect(10, 310, 201, 21))
        self.ProcessProgress.setValue(24)
        self.AnalysisResults = QTextEdit(self.page_2)
        self.AnalysisResults.setObjectName(u"AnalysisResults")
        self.AnalysisResults.setGeometry(QRect(250, 20, 601, 601))
        self.AnalysisResults.setReadOnly(True)
        self.ExportToPDFButton_2 = QPushButton(self.page_2)
        self.ExportToPDFButton_2.setObjectName(u"ExportToPDFButton_2")
        self.ExportToPDFButton_2.setGeometry(QRect(90, 280, 75, 24))
        self.PagePicker.addWidget(self.page_2)
        MainWindow.setCentralWidget(self.NavMenu)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1233, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.PagePicker.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Tender_Button.setText(QCoreApplication.translate("MainWindow", u"Tenders", None))
        self.AI_Analysis_Button.setText(QCoreApplication.translate("MainWindow", u"AI Analysis", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"BOM and Cost Estimator", None))
        self.TenderDetails.setTitle(QCoreApplication.translate("MainWindow", u"Detailed Tender Information", None))
        self.TenderName.setText(QCoreApplication.translate("MainWindow", u"Tender Name", None))
        self.ScrapeTendersButton.setText(QCoreApplication.translate("MainWindow", u"Scrape Tenders", None))
        self.ExportToPDFButton.setText(QCoreApplication.translate("MainWindow", u"Export to PDF", None))
        self.AddTenderButton.setText(QCoreApplication.translate("MainWindow", u"Add Tender", None))
        self.UploadFileButton.setText(QCoreApplication.translate("MainWindow", u"Upload", None))
        self.ExportToPDFButton_2.setText(QCoreApplication.translate("MainWindow", u"Export", None))
    # retranslateUi

