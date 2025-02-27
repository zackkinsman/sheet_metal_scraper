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
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QGroupBox,
    QHeaderView, QLabel, QLineEdit, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(943, 727)
        self.NavMenu = QWidget(MainWindow)
        self.NavMenu.setObjectName(u"NavMenu")
        self.Nav_Menu_Container = QFrame(self.NavMenu)
        self.Nav_Menu_Container.setObjectName(u"Nav_Menu_Container")
        self.Nav_Menu_Container.setGeometry(QRect(0, 0, 158, 104))
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

        self.TendeList = QTableWidget(self.NavMenu)
        if (self.TendeList.columnCount() < 4):
            self.TendeList.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.TendeList.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.TendeList.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.TendeList.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.TendeList.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.TendeList.setObjectName(u"TendeList")
        self.TendeList.setGeometry(QRect(160, 0, 491, 581))
        self.TenderDetails = QGroupBox(self.NavMenu)
        self.TenderDetails.setObjectName(u"TenderDetails")
        self.TenderDetails.setGeometry(QRect(660, 10, 282, 307))
        self.formLayout = QFormLayout(self.TenderDetails)
        self.formLayout.setObjectName(u"formLayout")
        self.TenderName = QLabel(self.TenderDetails)
        self.TenderName.setObjectName(u"TenderName")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.TenderName)

        self.Date = QLineEdit(self.TenderDetails)
        self.Date.setObjectName(u"Date")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.Date)

        self.TenderDescription = QTextEdit(self.TenderDetails)
        self.TenderDescription.setObjectName(u"TenderDescription")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.TenderDescription)

        self.pushButton = QPushButton(self.TenderDetails)
        self.pushButton.setObjectName(u"pushButton")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.pushButton)

        self.ScrapeTendersButton = QPushButton(self.NavMenu)
        self.ScrapeTendersButton.setObjectName(u"ScrapeTendersButton")
        self.ScrapeTendersButton.setGeometry(QRect(160, 590, 88, 24))
        self.MarkAsInterestedButton = QPushButton(self.NavMenu)
        self.MarkAsInterestedButton.setObjectName(u"MarkAsInterestedButton")
        self.MarkAsInterestedButton.setGeometry(QRect(250, 590, 106, 24))
        self.ExportToPDFButton = QPushButton(self.NavMenu)
        self.ExportToPDFButton.setObjectName(u"ExportToPDFButton")
        self.ExportToPDFButton.setGeometry(QRect(360, 590, 81, 24))
        MainWindow.setCentralWidget(self.NavMenu)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 943, 33))
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
        ___qtablewidgetitem = self.TendeList.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Name", None));
        ___qtablewidgetitem1 = self.TendeList.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Date Posted", None));
        ___qtablewidgetitem2 = self.TendeList.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Closing Date", None));
        ___qtablewidgetitem3 = self.TendeList.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Status", None));
        self.TenderDetails.setTitle(QCoreApplication.translate("MainWindow", u"GroupBox", None))
        self.TenderName.setText(QCoreApplication.translate("MainWindow", u"Tender Name", None))
        self.Date.setText(QCoreApplication.translate("MainWindow", u"Date", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"View Full Details", None))
        self.ScrapeTendersButton.setText(QCoreApplication.translate("MainWindow", u"Scrape Tenders", None))
        self.MarkAsInterestedButton.setText(QCoreApplication.translate("MainWindow", u"Mark as Interested", None))
        self.ExportToPDFButton.setText(QCoreApplication.translate("MainWindow", u"Export to PDF", None))
    # retranslateUi

