from __future__ import print_function
from collections import namedtuple
from datetime import datetime
import logging

# Third party imports
from sqlalchemy import Table, Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_mixins import AllFeaturesMixin


log = logging.getLogger(__name__)
Base = declarative_base()


class BaseModel(Base, AllFeaturesMixin):
    __abstract__ = True
    pass


class User(UserMixin, BaseModel):
    __tablename__ = 'users'

    id = Column(Integer(), primary_key=True)
    username = Column(String(64), index=True, unique=True)
    email = Column(String(120), index=True, unique=True)
    password_hash = Column(String(128))
    # profile = relationship('Profile', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Profile(BaseModel):
    __tablename__ = 'profiles'

    profile_id = Column(Integer, primary_key=True)
    body = Column(String(255))
    user_id = Column(Integer(), ForeignKey('users.id'))

    # user = relationship("User", backref=backref('profiles', order_by=profile_id))

    def __repr__(self):
        return '<Profile {}>'.format(self.body)


class MyMixin(object):

	@declared_attr
	def __tablename__(cls): # pylint: disable=E0213
		return cls.__name__.lower()

	__table_args__ = {'mysql_engine': 'Sqlite'}
	__mapper_args__ = {'always_refresh': True}

	id = Column(Integer(), primary_key=True)
	MTS = Column(DateTime(), nullable=False)
	Open = Column(Float(), nullable=False)
	Close = Column(Float(), nullable=False)
	High = Column(Float(), nullable=False)
	Low = Column(Float(), nullable=False)
	Volume = Column(Float(), nullable=False)

	def __repr__(self):
		return f"{self.__tablename__} <MTS={self.MTS},  Close={self.Close}>"


class Avt(MyMixin, BaseModel):
    pass

class Bch(MyMixin, BaseModel):
    pass

class Btc(MyMixin, BaseModel):
    pass

class Btg(MyMixin, BaseModel):
    pass

class Dsh(MyMixin, BaseModel):
    pass

class Eos(MyMixin, BaseModel):
    pass

class Etc(MyMixin, BaseModel):
    pass

class Eth(MyMixin, BaseModel):
    pass

class Fun(MyMixin, BaseModel):
    pass

class Gnt(MyMixin, BaseModel):
    pass

class Iot(MyMixin, BaseModel):
    pass

class Ltc(MyMixin, BaseModel):
    pass

class Neo(MyMixin, BaseModel):
    pass

class Qsh(MyMixin, BaseModel):
    pass

class Qtm(MyMixin, BaseModel):
    pass

class Omg(MyMixin, BaseModel):
    pass

class Rcn(MyMixin, BaseModel):
    pass

class Rlc(MyMixin, BaseModel):
    pass

class San(MyMixin, BaseModel):
    pass

class Spk(MyMixin, BaseModel):
    pass

class Trx(MyMixin, BaseModel):
    pass

class Xlm(MyMixin, BaseModel):
    pass

class Xmr(MyMixin, BaseModel):
    pass

class Ada(MyMixin, BaseModel):
    pass

class Xvg(MyMixin, BaseModel):
    pass

class Xem(MyMixin, BaseModel):
    pass

class Ven(MyMixin, BaseModel):
    pass

class Bnb(MyMixin, BaseModel):
    pass

class Bcn(MyMixin, BaseModel):
    pass

class Icx(MyMixin, BaseModel):
    pass

class Lsk(MyMixin, BaseModel):
    pass

class Zil(MyMixin, BaseModel):
    pass

class Ont(MyMixin, BaseModel):
    pass

class Ae(MyMixin, BaseModel):
    pass

class Zrx(MyMixin, BaseModel):
    pass

class Dcr(MyMixin, BaseModel):
    pass

class Nano(MyMixin, BaseModel):
    pass

class Waves(MyMixin, BaseModel):
    pass

class Xrp(MyMixin, BaseModel):
    pass

class Zec(MyMixin, BaseModel):
    pass

class Elf(MyMixin, BaseModel):
    pass

class Steem(MyMixin, BaseModel):
    pass

class Mana(MyMixin, BaseModel):
    pass

class Edo(MyMixin, BaseModel):
    pass


CryptoCompare_DB_Tables = {
    'avt': Avt,
    'ada': Ada,
    'xvg': Xvg,
    'xem': Xem,
    'ven': Ven,
    'bnb': Bnb,
    'bcn': Bcn,
    'icx': Icx,
    'lsk': Lsk,
    'zil': Zil,
    'ont': Ont,
    'ae': Ae,
    'zrx': Zrx,
    'dcr': Dcr,
    'nano': Nano,
    'waves': Waves,
    'steem': Steem,
    'rcn': Rcn,
    'rlc': Rlc,
    'elf': Elf,
    'mana': Mana
}

DB_Tables = {
    'bch': Bch,
    'btc': Btc,
    'btg': Btg,
    'dsh': Dsh,
    'eos': Eos,
    'etc': Etc,
    'eth': Eth,
    'fun': Fun,
    'gnt': Gnt,
    'iot': Iot,
    'ltc': Ltc,
    'neo': Neo,
    'omg': Omg,
    'qsh': Qsh,
    'qtm': Qtm,
    'san': San,
    'spk': Spk,
    'trx': Trx,
    'xlm': Xlm,
    'xmr': Xmr,
    'xrp': Xrp,
    'zec': Zec,
    'edo': Edo
}


def all_DB_tables():
    return {**CryptoCompare_DB_Tables, **DB_Tables}


def getTable(coin):
	return all_DB_tables()[coin]


# weird code makes dict into an object
# table = namedtuple('DB_Tables', all_DB_tables().keys())(**all_DB_tables())
