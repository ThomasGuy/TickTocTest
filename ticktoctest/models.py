# Third party imports
from sqlalchemy import Table, Column, DateTime, Float, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.declarative import declarative_base, declared_attr
# from flask_sqlalchemy_session import current_session as cs
# from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer(), primary_key=True)
    username = Column(String(64), index=True, unique=True, nullable=False)
    email = Column(String(120), index=True, unique=True, nullable=False)
    password_hash = Column(String(128))

    # 1 to 1 relationship with Portfolio
    portfolio = relationship("Portfolio", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return '<User {}>'.format(self.username)

    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)

    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)


class Portfolio(Base):
    __tablename__ = 'portfolios'

    id = Column(Integer, primary_key=True)
    sma = Column(Integer, nullable=False)
    bma = Column(Integer, nullable=False)
    lma = Column(Integer, nullable=False)
    freq = Column(String(3), nullable=False)

    # 1 to 1 relationship with User
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User")
    # 1 to many relationship with bank
    bank = relationship("Bank", cascade="all, delete, delete-orphan")

    def __init__(self, sma=20, bma=55, lma=140, freq='6h'):
        self.sma = sma
        self.bma = bma
        self.lma = lma
        self.freq = freq

    def __repr__(self):
        return "<Portfolio (sma={}, bma={}, lma={}, freq={})>".format(self.sma, self.bma, self.lma, self.freq)

    @hybrid_property
    def my_portfolio(self):
        return [(row.coin_id, row.amount) for row in self.bank]

    @hybrid_method
    def i_have(self, altcoin):
        for row in self.bank:
            if row.coin_id == altcoin:
                return True
        return False

    @hybrid_method
    def amount(self, altcoin):
        for row in self.bank:
            if row.coin_id == altcoin:
                return row.amount


class Bank(Base):
    __tablename__ = 'banks'

    amount = Column(Float, nullable=False)
    # 1 to many from Portfolio
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), primary_key=True)
    # many to 1 to Coins
    coin_id = Column(String(6), ForeignKey('coins.coin'), primary_key=True)
    # relationship with Coin
    altcoin = relationship("Coin", cascade="all, delete")

    def __repr__(self):
        return "<Bank (amount={}, Coin={})>".format(self.amount, self.coin_id)


class Coin(Base):
    __tablename__ = 'coins'

    coin = Column(String(6), primary_key=True)
    name = Column(String(40), nullable=False, unique=True)
    rank = Column(Integer)
    market_cap = Column(Float)


class MyMixin(object):

    @declared_attr
    def __tablename__(cls):  # pylint: disable=E0213
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'innoDB'}
    __mapper_args__ = {'always_refresh': True}

    id = Column(Integer(), primary_key=True)
    MTS = Column(DateTime(), nullable=False)
    Open = Column(Float(), nullable=False)
    Close = Column(Float(), nullable=False)
    High = Column(Float(), nullable=False)
    Low = Column(Float(), nullable=False)
    Volume = Column(Float(), nullable=False)

    def __repr__(self):
        return f"{self.__tablename__} <MTS={self.MTS}, Open={self.Open}, Close={self.Close}, High={self.High}, \
                 Low={self.Low}, Volume={self.Volume}>"


class Ada(MyMixin, Base):
    name = 'Cardano (ADA)'


class Ae(MyMixin, Base):
    name = 'Aeternity (AE)'


class Avt(MyMixin, Base):
    name = 'Aventus (AVT)'


class Bab(MyMixin, Base):
    name = 'Bitcoin Cash ABC (BAB)'


class Bch(MyMixin, Base):
    name = 'Bitcoin Cash (BCH)'


class Bchsv(MyMixin, Base):
    name = 'Bitcoin Cash SV (BCHSV)'


class Bcn(MyMixin, Base):
    name = 'Bytecoin (BCN)'


class Bnb(MyMixin, Base):
    name = 'Binance Coin (BNB)'


class Btc(MyMixin, Base):
    name = 'Bitcoin (BTC)'


class Btg(MyMixin, Base):
    name = 'Bitcoin Gold (BTG)'


class Dcr(MyMixin, Base):
    name = 'Decred (DCR)'


class Dsh(MyMixin, Base):
    name = 'Dash (DSH)'


class Edo(MyMixin, Base):
    name = 'Eidoo (EDO)'


class Elf(MyMixin, Base):
    name = 'aelf (ELF)'


class Eos(MyMixin, Base):
    name = 'Eosio (EOS)'


class Etc(MyMixin, Base):
    name = 'Ethereum Classic (ETC)'


class Eth(MyMixin, Base):
    name = 'Ethereum (ETH)'


class Fun(MyMixin, Base):
    name = 'FunFair (FUN)'


class Gnt(MyMixin, Base):
    name = 'Golem (GNT)'


class Icx(MyMixin, Base):
    name = 'ICON (ICX)'


class Iot(MyMixin, Base):
    name = 'Iota (IOT)'


class Lsk(MyMixin, Base):
    name = 'Lisk (LSK)'


class Ltc(MyMixin, Base):
    name = 'Litecoin (LTC)'


class Mana(MyMixin, Base):
    name = 'Decentraland (MANA)'


class Nano(MyMixin, Base):
    name = 'Nano (NANO)'


class Neo(MyMixin, Base):
    name = 'Neon (NEO)'


class Omg(MyMixin, Base):
    name = 'Omisego (OMG)'


class Ont(MyMixin, Base):
    name = 'Ontology (ONT)'


class Qsh(MyMixin, Base):
    name = 'QASH (QSH)'


class Qtm(MyMixin, Base):
    name = 'Qtum (QTM)'


class Rcn(MyMixin, Base):
    name = 'Ripio Credit Network (RCN)'


class Rlc(MyMixin, Base):
    name = 'iExec (RLC)'


class San(MyMixin, Base):
    name = 'Santiment (SAN)'


class Spk(MyMixin, Base):
    name = 'SpankChain (SPK)'


class Steem(MyMixin, Base):
    name = 'Steem (STEEM)'


class Trx(MyMixin, Base):
    name = 'Tron (TRX)'


class Ven(MyMixin, Base):
    name = 'VeChain (VEN)'


class Waves(MyMixin, Base):
    name = 'Waves (WAVES)'


class Xem(MyMixin, Base):
    name = 'Xem (XEM)'


class Xlm(MyMixin, Base):
    name = 'Stella Lumen (XLM)'


class Xmr(MyMixin, Base):
    name = 'Monero (XMR)'


class Xrp(MyMixin, Base):
    name = 'Ripple (XRP)'


class Xvg(MyMixin, Base):
    name = 'Verge (XVG)'


class Zec(MyMixin, Base):
    name = 'Zcash (ZEC)'


class Zil(MyMixin, Base):
    name = 'Zilliqa (ZIL)'


class Zrx(MyMixin, Base):
    name = 'Ox (ZRX)'


Binance_Tables = {
    '15m': {
        'bchsv': Bchsv
    },
    '1h': {
    },
    '3h': {
    }
}

CryptoCompare_Tables = {
    '15m': {
        'ada': Ada,
        'bch': Bch,
        'ae': Ae,
        'bnb': Bnb,
        'bcn': Bcn,
        'icx': Icx,
        'ont': Ont,
        'omg': Omg,
        'trx': Trx,
        'xem': Xem,
        'zil': Zil,
        'zrx': Zrx
    },
    '1h': {
        'dcr': Dcr,
        'lsk': Lsk,
        'nano': Nano,
        'steem': Steem,
        'ven': Ven,
        'waves': Waves,
        'xvg': Xvg
    },
    '3h': {
        'mana': Mana
    }
}

Bitfinex_Tables = {
    '15m': {
        'btc': Btc,
        'bab': Bab,
        'btg': Btg,
        'dsh': Dsh,
        'eos': Eos,
        'etc': Etc,
        'eth': Eth,
        'iot': Iot,
        'ltc': Ltc,
        'neo': Neo,
        'xlm': Xlm,
        'xmr': Xmr,
        'xrp': Xrp,
        'zec': Zec
    },
    '1h': {
        'edo': Edo,
        'elf': Elf,
        'gnt': Gnt,
        'qsh': Qsh,
        'qtm': Qtm,
        'san': San
    },
    '3h': {
        'avt': Avt,
        'fun': Fun,
        'rcn': Rcn,
        'rlc': Rlc,
        'spk': Spk
    }
}


def all_DB_tables():
    compare = {**CryptoCompare_Tables['15m'], **CryptoCompare_Tables['1h'], **CryptoCompare_Tables['3h']}
    bitfinex = {**Bitfinex_Tables['15m'], **Bitfinex_Tables['1h'], **Bitfinex_Tables['3h']}
    binance = {**Binance_Tables['15m'], **Binance_Tables['1h'], **Binance_Tables['3h']}
    return {**compare, **bitfinex, **binance}


def getTable(coin):
    return all_DB_tables()[coin]


def delta_tables(delta):
    return {**Bitfinex_Tables[delta], **CryptoCompare_Tables[delta], **Binance_Tables[delta]}
