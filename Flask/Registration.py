class Registration:
    # Per usare la classe: passare al costruttore direttamente il cursore di una connessione a mysql già stabilita
    # user, pwd, lat, lon
    def __init__(self, cur):
        self.cur = cur

    @staticmethod
    def lat_lon_control(lat, lon):
        try:
            lat = float(lat)
            lon = float(lon)
        except Exception as e:
            print(e)
            return 'Error: use dot not comma'

        if (lat < -90) or (lat > 90):
            return 'Insert a correct latitude (-90/90)'
        elif (lon < -180) or (lon > 180):
            return 'Insert a correct longitude (-180/180)'

        return "True"

    @staticmethod
    def check_pwd(pwd):
        if len(pwd) < 8:
            return False
        return True

    def check_db(self, username, password):
        if username is None or password is None:
            return 'Please insert a correct user and a correct password'

        if not self.check_pwd(password):
            return 'Please insert a correct password (at least 8 characters)'

        # seleziona user e pin
        query = f"select user_name " \
                f"from rack_user "
        self.cur.execute(query)
        result = self.cur.fetchall()

        print(result)

        if not result:
            return 'Please insert a correct user and a correct password'

        for i in result:
            # print(i[0], username)
            if i[0] == username:
                return 'Username already in use'

        return "True"
