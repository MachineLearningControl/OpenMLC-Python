#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "ui_experiment.h"

#include <QDialog>
#include <iostream>

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::on_experiment_list_clicked(const QModelIndex &index)
{

}
