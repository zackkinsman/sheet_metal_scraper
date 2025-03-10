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
    QHeaderView, QLabel, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTableView,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1213, 774)
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

        self.TenderDetails = QGroupBox(self.NavMenu)
        self.TenderDetails.setObjectName(u"TenderDetails")
        self.TenderDetails.setGeometry(QRect(900, 20, 282, 571))
        self.TenderName = QLabel(self.TenderDetails)
        self.TenderName.setObjectName(u"TenderName")
        self.TenderName.setGeometry(QRect(10, 26, 71, 16))
        self.TenderExpandedInfo = QTextEdit(self.TenderDetails)
        self.TenderExpandedInfo.setObjectName(u"TenderExpandedInfo")
        self.TenderExpandedInfo.setGeometry(QRect(10, 50, 261, 511))
        self.TenderList = QTableView(self.NavMenu)
        self.TenderList.setObjectName(u"TenderList")
        self.TenderList.setGeometry(QRect(190, 30, 701, 561))
        self.layoutWidget = QWidget(self.NavMenu)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(190, 600, 258, 26))
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

        MainWindow.setCentralWidget(self.NavMenu)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1213, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Tender_Button.setText(QCoreApplication.translate("MainWindow", u"Tenders", None))
        self.AI_Analysis_Button.setText(QCoreApplication.translate("MainWindow", u"AI Analysis", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"BOM and Cost Estimator", None))
        self.TenderDetails.setTitle(QCoreApplication.translate("MainWindow", u"GroupBox", None))
        self.TenderName.setText(QCoreApplication.translate("MainWindow", u"Tender Name", None))
        self.ScrapeTendersButton.setText(QCoreApplication.translate("MainWindow", u"Scrape Tenders", None))
        self.ExportToPDFButton.setText(QCoreApplication.translate("MainWindow", u"Export to PDF", None))
        self.AddTenderButton.setText(QCoreApplication.translate("MainWindow", u"Add Tender", None))
    # retranslateUi

