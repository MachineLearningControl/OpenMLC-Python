def stmt_create_table_board():
    return ''' CREATE TABLE board(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  board_type TEXT,
                                  connection_type INTEGER,
                                  read_count INTEGER,
                                  read_delay INTEGER,
                                  report_mode INTEGER,
                                  analog_resolution INTEGER)'''


def stmt_create_table_serial_connection():
    return ''' CREATE TABLE serial_connection(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                              board_id INTEGER,
                                              port INTEGER,
                                              baudrate INTEGER,
                                              parity INTEGER,
                                              stopbits INTEGER,
                                              bytesize INTEGER,
                                              FOREIGN KEY(board_id) REFERENCES board(id))'''


def stmt_create_table_digital_pin():
    return ''' CREATE TABLE digital_pin(pin_id INTEGER,
                                        board_id INTEGER,
                                        pin_type INTEGER,
                                        PRIMARY KEY (pin_id, board_id),
                                        FOREIGN KEY(board_id) REFERENCES board(id))'''


def stmt_create_table_analog_pin():
    return ''' CREATE TABLE analog_pin(pin_id INTEGER,
                                       board_id INTEGER,
                                       pin_type INTEGER,
                                       PRIMARY KEY (pin_id, board_id),
                                       FOREIGN KEY(board_id) REFERENCES board(id))'''


def stmt_create_table_pwm_pin():
    return ''' CREATE TABLE pwm_pin(pin_id INTEGER,
                                    board_id INTEGER,
                                    PRIMARY KEY (pin_id, board_id),
                                    FOREIGN KEY(board_id) REFERENCES board(id))'''

def stmt_insert_board(board_type, connection_type, read_count, read_delay, report_mode, analog_resolution):
    return '''INSERT INTO board (board_type, connection_type, read_count, read_delay, report_mode, analog_resolution)
              VALUES ("%s", %s, %s, %s, %s, %s)''' % (board_type,
                                                      connection_type,
                                                      read_count,
                                                      read_delay,
                                                      report_mode,
                                                      analog_resolution)

def stmt_update_board(board_id, board_type, connection_type, read_count, read_delay, report_mode, analog_resolution):
    return '''UPDATE board SET
              board_type = "%s",
              connection_type = %s,
              read_count = %s,
              read_delay = %s,
              report_mode = %s,
              analog_resolution = %s
              WHERE id = %s''' % (board_type,
                                  connection_type,
                                  read_count,
                                  read_delay,
                                  report_mode,
                                  analog_resolution,
                                  board_id)


def stmt_get_board(board_id):
    return '''SELECT board_type, report_mode, read_count, read_delay, analog_resolution
              FROM board WHERE id = %s''' % board_id


def stmt_delete_digital_pin(board_id):
    return __stmt_delete_pin("digital_pin", board_id)


def stmt_delete_analog_pin(board_id):
    return __stmt_delete_pin("analog_pin", board_id)


def stmt_delete_pwm_pin(board_id):
    return __stmt_delete_pin("pwm_pin", board_id)


def __stmt_delete_pin(pin_table, board_id):
    return '''DELETE FROM %s WHERE board_id = %s''' % (pin_table, board_id)


def stmt_insert_digital_pin(board_id, pin_id, pin_type):
    return __stmt_insert_pin("digital_pin", board_id, pin_id, pin_type)


def stmt_insert_analog_pin(board_id, pin_id, pin_type):
    return __stmt_insert_pin("analog_pin", board_id, pin_id, pin_type)


def __stmt_insert_pin(pin_table, board_id, pin_id, pin_type):
    return '''INSERT INTO %s (pin_id, board_id, pin_type) VALUES (%s, %s, %s)''' % (pin_table, pin_id, board_id, pin_type)


def stmt_insert_pwm_pin(board_id, pin_id):
    return '''INSERT INTO pwm_pin (pin_id, board_id) VALUES (%s, %s)''' % (pin_id, board_id)


def stmt_get_analog_pins(board_id):
    return "SELECT pin_id, pin_type FROM analog_pin WHERE board_id = %s" % (board_id)


def stmt_get_digital_pins(board_id):
    return "SELECT pin_id, pin_type FROM digital_pin WHERE board_id = %s" % (board_id)


def stmt_get_pwm_pins(board_id):
    return "SELECT pin_id FROM pwm_pin WHERE board_id = %s" % (board_id)


def stmt_insert_serial_connection(board_id, port, baudrate, parity, stopbits, bytesize):
    return '''INSERT INTO serial_connection (board_id, port, baudrate, parity, stopbits, bytesize)
              VALUES (%s, %s, %s, %s, %s, %s)''' % (board_id,
                                                    port,
                                                    baudrate,
                                                    parity,
                                                    stopbits,
                                                    bytesize)

def stmt_update_serial_connection(connection_id, board_id, port, baudrate, parity, stopbits, bytesize):
    return '''UPDATE serial_connection SET
              board_id = "%s",
              port = %s,
              baudrate = %s,
              parity = %s,
              stopbits = %s,
              bytesize = %s
              WHERE id = %s''' % (board_id,
                                  port,
                                  baudrate,
                                  parity,
                                  stopbits,
                                  bytesize,
                                  connection_id)

def stmt_get_serial_connection(board_id):
    return '''SELECT port, baudrate, parity, stopbits, bytesize
              FROM serial_connection WHERE board_id = %s''' % board_id