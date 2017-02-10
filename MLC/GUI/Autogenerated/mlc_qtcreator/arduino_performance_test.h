#ifndef ARDUINO_PERFORMANCE_TEST_H
#define ARDUINO_PERFORMANCE_TEST_H

#include <QDialog>

namespace Ui {
class arduino_performance_test;
}

class arduino_performance_test : public QDialog
{
    Q_OBJECT

public:
    explicit arduino_performance_test(QWidget *parent = 0);
    ~arduino_performance_test();

private:
    Ui::arduino_performance_test *ui;
};

#endif // ARDUINO_PERFORMANCE_TEST_H
