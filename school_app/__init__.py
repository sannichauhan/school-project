import pymysql

pymysql.version_info = (1, 4, 3, "final", 0)  # Django ke version check ko bypass karne ke liye
pymysql.install_as_MySQLdb()
