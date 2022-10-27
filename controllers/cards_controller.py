from flask import Blueprint, request
from init import db
from datetime import date
from models.card import Card, CardSchema
from models.comment import Comment, CommentSchema
from controllers.auth_controller import authorize
from flask_jwt_extended import jwt_required, get_jwt_identity

cards_bp = Blueprint('cards', __name__, url_prefix='/cards')

@cards_bp.route('/')
# @jwt_required()
def get_all_cards():
    # return 'all_cards route'
    # if not authorize():
    #     return {'error': 'You must be an admin'}, 401
    stmt = db.select(Card).order_by(Card.date.desc())
    cards = db.session.scalars(stmt)
    return CardSchema(many=True).dump(cards)

@cards_bp.route('/<int:id>/')
def get_one_card(id):
    stmt = db.select(Card).filter_by(id=id)
    card = db.session.scalar(stmt)
    if card:
        return CardSchema().dump(card)
    return {'error': f'card not found with id {id}'}, 404

@cards_bp.route('/<int:id>/', methods=['DELETE'])
@jwt_required()
def delete_one_card(id):
    authorize()
    stmt = db.select(Card).filter_by(id=id)
    card = db.session.scalar(stmt)
    if card:
        db.session.delete(card)
        db.session.commit()
        return {'message': f'Card {card.title} deleted successfully'}
    return {'error': f'card not found with id {id}'}, 404

@cards_bp.route('/<int:id>/', methods=['PUT', 'PATCH']) # PUT = whole object and all fields, PATCH = only some fields passsed
@jwt_required()
def update_one_card(id):
    stmt = db.select(Card).filter_by(id=id)
    card = db.session.scalar(stmt)
    if card:
        card.title = request.json.get('title') or card.title
        card.description = request.json.get('description') or card.description
        card.status = request.json.get('status') or card.status
        card.priority = request.json.get('priority') or card.priority
        db.session.commit() # card already in db so don't have to add, just commit changes
        return CardSchema().dump(card)
    return {'error': f'card not found with id {id}'}, 404

@cards_bp.route('/', methods=['POST'])
@jwt_required()
def create_card():
    # Create a new Card model instance
    data = CardSchema().load(request.json)

    card = Card(
        title = data['title'],
        description = data['description'],
        date = date.today(),
        status = data['status'],
        priority = data['priority'],
        user_id = get_jwt_identity()
    )
    # Add and commit user to DB
    db.session.add(card)
    db.session.commit()
    # Respond to client
    return CardSchema().dump(card), 201

@cards_bp.route('/<int:card_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(card_id):
    # Create a new Comment model instance
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card:
        comment = Comment(
                message = request.json['message'],
                user_id = get_jwt_identity(),
                card = card,
                date = date.today()
        )
        # Add and commit user to DB
        db.session.add(comment)
        db.session.commit()
        return CommentSchema().dump(comment)
    return {'error': f'card not found with id {id}'}, 404
