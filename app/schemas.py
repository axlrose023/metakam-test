from . import ma
from .models import Cake, Bakery
from marshmallow import validates, ValidationError

class CakeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cake
        include_fk = True
        load_instance = True

    @validates('price')
    def validate_price(self, value):
        if value < 0:
            raise ValidationError('Price must be a positive number.')

class BakerySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Bakery
        include_fk = True
        load_instance = True

    @validates('rating')
    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise ValidationError('Rating must be between 1 and 5.')
