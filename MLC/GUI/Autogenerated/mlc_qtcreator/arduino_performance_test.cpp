#include "arduino_performance_test.h"
#include "ui_arduino_performance_test.h"

arduino_performance_test::arduino_performance_test(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::arduino_performance_test)
{
    ui->setupUi(this);
}

arduino_performance_test::~arduino_performance_test()
{
    delete ui;
}
