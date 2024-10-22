from . import db
from sqlalchemy.ext.declarative import declared_attr


class BaseModel(db.Model):
    __abstract__ = True

    @declared_attr
    def id(cls):
        return db.Column(db.Integer, primary_key=True)


cakes_bakeries = db.Table('cakes_bakeries',
                          db.Column('cake_id', db.Integer, db.ForeignKey('cake.id'), primary_key=True),
                          db.Column('bakery_id', db.Integer, db.ForeignKey('bakery.id'), primary_key=True)
                          )


class Cake(BaseModel):
    __tablename__ = 'cake'

    name = db.Column(db.String(100), nullable=False)
    flavor = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, default=True)
    bakeries = db.relationship('Bakery', secondary=cakes_bakeries, back_populates='cakes')


class Bakery(BaseModel):
    __tablename__ = 'bakery'

    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    cakes = db.relationship('Cake', secondary=cakes_bakeries, back_populates='bakeries')
