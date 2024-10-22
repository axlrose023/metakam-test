from flask import Blueprint, request, jsonify, current_app
from .models import db, Cake, Bakery
from .schemas import CakeSchema, BakerySchema
from werkzeug.exceptions import NotFound, BadRequest
from marshmallow import ValidationError

api_bp = Blueprint('api', __name__)

cake_schema = CakeSchema()
cakes_schema = CakeSchema(many=True)
bakery_schema = BakerySchema()
bakeries_schema = BakerySchema(many=True)


@api_bp.app_errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({'error': error.messages}), 400


@api_bp.app_errorhandler(404)
def handle_not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404


@api_bp.app_errorhandler(500)
def handle_internal_error(error):
    current_app.logger.error(f'Server Error: {error}, Path: {request.path}')
    return jsonify({'error': 'An unexpected error occurred'}), 500


@api_bp.route('/api/v1/trigger-500', methods=['GET'])
def trigger_internal_server_error():
    raise Exception("This is a test exception")


@api_bp.route('/api/v1/cakes', methods=['GET'])
def get_cakes():
    flavor = request.args.get('flavor')
    max_price = request.args.get('max_price', type=float)
    page = request.args.get('page', type=int)
    limit = request.args.get('limit', type=int)

    query = Cake.query
    if flavor:
        query = query.filter(Cake.flavor.ilike(f'%{flavor}%'))

    if max_price is not None:
        query = query.filter(Cake.price <= max_price)

    if page is not None and limit is not None:
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        cakes = pagination.items
        total_pages = pagination.pages
        total_items = pagination.total

        result = {
            'cakes': cakes_schema.dump(cakes),
            'total_pages': total_pages,
            'total_items': total_items,
            'current_page': page
        }
        return jsonify(result), 200
    else:
        # No pagination, return all results
        cakes = query.all()
        return cakes_schema.jsonify(cakes), 200


@api_bp.route('/api/v1/cakes/<int:id>', methods=['GET'])
def get_cake(id):
    cake = Cake.query.get_or_404(id)
    return cake_schema.jsonify(cake), 200


@api_bp.route('/api/v1/cakes', methods=['POST'])
def create_cake():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        cake = cake_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    db.session.add(cake)
    db.session.commit()
    return cake_schema.jsonify(cake), 201


@api_bp.route('/api/v1/cakes/<int:id>', methods=['PUT'])
def update_cake(id):
    cake = Cake.query.get_or_404(id)
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        cake = cake_schema.load(json_data, instance=cake, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    db.session.commit()
    return cake_schema.jsonify(cake), 200


@api_bp.route('/api/v1/cakes/<int:id>', methods=['DELETE'])
def delete_cake(id):
    cake = Cake.query.get_or_404(id)
    db.session.delete(cake)
    db.session.commit()
    return jsonify({'message': 'Cake deleted successfully'}), 200


@api_bp.route('/api/v1/bakeries', methods=['GET'])
def get_bakeries():
    bakeries = Bakery.query.all()
    return bakeries_schema.jsonify(bakeries), 200


@api_bp.route('/api/v1/bakeries/<int:id>', methods=['GET'])
def get_bakery(id):
    bakery = Bakery.query.get_or_404(id)
    return bakery_schema.jsonify(bakery), 200


@api_bp.route('/api/v1/bakeries', methods=['POST'])
def create_bakery():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        bakery = bakery_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    db.session.add(bakery)
    db.session.commit()
    return bakery_schema.jsonify(bakery), 201


@api_bp.route('/api/v1/bakeries/<int:id>', methods=['PUT'])
def update_bakery(id):
    bakery = Bakery.query.get_or_404(id)
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        bakery = bakery_schema.load(json_data, instance=bakery, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    db.session.commit()
    return bakery_schema.jsonify(bakery), 200


@api_bp.route('/api/v1/bakeries/<int:id>', methods=['DELETE'])
def delete_bakery(id):
    bakery = Bakery.query.get_or_404(id)
    db.session.delete(bakery)
    db.session.commit()
    return jsonify({'message': 'Bakery deleted successfully'}), 200


@api_bp.route('/api/v1/cakes/<int:cake_id>/bakeries/<int:bakery_id>', methods=['POST'])
def add_bakery_to_cake(cake_id, bakery_id):
    cake = Cake.query.get_or_404(cake_id)
    bakery = Bakery.query.get_or_404(bakery_id)
    if bakery not in cake.bakeries:
        cake.bakeries.append(bakery)
        db.session.commit()
    return jsonify({'message': 'Bakery added to cake'}), 200


@api_bp.route('/api/v1/cakes/<int:cake_id>/bakeries/<int:bakery_id>', methods=['DELETE'])
def remove_bakery_from_cake(cake_id, bakery_id):
    cake = Cake.query.get_or_404(cake_id)
    bakery = Bakery.query.get_or_404(bakery_id)
    if bakery in cake.bakeries:
        cake.bakeries.remove(bakery)
        db.session.commit()
    return jsonify({'message': 'Bakery removed from cake'}), 200


@api_bp.route('/api/v1/bakeries/<int:bakery_id>/cakes', methods=['GET'])
def get_cakes_by_bakery(bakery_id):
    bakery = Bakery.query.get_or_404(bakery_id)
    flavor = request.args.get('flavor')
    max_price = request.args.get('max_price', type=float)
    page = request.args.get('page', type=int)
    limit = request.args.get('limit', type=int)

    query = Cake.query.join(Cake.bakeries).filter(Bakery.id == bakery_id)
    if flavor:
        query = query.filter(Cake.flavor.ilike(f'%{flavor}%'))

    if max_price is not None:
        query = query.filter(Cake.price <= max_price)

    if page is not None and limit is not None:
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        cakes = pagination.items
        total_pages = pagination.pages
        total_items = pagination.total

        result = {
            'cakes': cakes_schema.dump(cakes),
            'total_pages': total_pages,
            'total_items': total_items,
            'current_page': page
        }
        return jsonify(result), 200
    else:
        cakes = query.all()
        return cakes_schema.jsonify(cakes), 200
