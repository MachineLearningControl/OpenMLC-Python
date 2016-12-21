#-------------------------------------------------
#
# Project created by QtCreator 2016-11-20T20:09:48
#
#-------------------------------------------------

QT       += core gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = untitled
TEMPLATE = app


SOURCES += main.cpp\
        mainwindow.cpp

HEADERS  += mainwindow.h

FORMS    += \
    mainwindow.ui \
    experiment.ui \
    edit_properties.ui \
    experiment_in_progress.ui

DISTFILES += \
    New_projectForm.ui.qml \
    New_project.qml

STATECHARTS += \
    zaraza.scxml
