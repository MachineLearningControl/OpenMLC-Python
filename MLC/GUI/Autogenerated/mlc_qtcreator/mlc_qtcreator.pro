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
        mainwindow.cpp \
    arduino_performance_test.cpp

HEADERS  += mainwindow.h \
    arduino_performance_test.h

FORMS    += \
    mainwindow.ui \
    experiment.ui \
    edit_properties.ui \
    experiment_in_progress.ui \
    genealogy.ui \
    board_config_design.ui \
    arduinoconnectiontest.ui  \
    pinout_design.ui \ 
    arduino_performance_test.ui \
    about.ui \
    generic_spinner.ui

DISTFILES +=
