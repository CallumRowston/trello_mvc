from init import db, ma
from marshmallow import fields, validates
from marshmallow.validate import Length, OneOf, And, Regexp
from marshmallow.exceptions import ValidationError

VALID_PRIORITIES = ('Urgent', 'High', 'Low', 'Medium')
VALID_STATUSES = ('To Do', 'Done', 'Ongoing', 'Testing', 'Deployed')

class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.Date) # Date created
    status = db.Column(db.String, default=VALID_STATUSES[0])
    priority = db.Column(db.String, default=VALID_PRIORITIES[0]) # Default in model incase model used without schema (eg when seeding)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='cards')
    comments = db.relationship('Comment', back_populates='card', cascade='all, delete')

class CardSchema(ma.Schema):
    user = fields.Nested('UserSchema', only=['name', 'email'])
    comments = fields.List(fields.Nested('CommentSchema', exclude=['card']))
    title = fields.String(required=True, validate=And(
        Length(min=2, error='Title must be at least 2 characters long'), 
        Regexp('^[a-zA-Z0-9]+$', error='Only letters, numbers and spaces are allowed')))
    status = fields.String(load_default=VALID_STATUSES[0], validate=OneOf(VALID_STATUSES))
    priority = fields.String(required=True, validate=OneOf(VALID_PRIORITIES)) # Default in schema for validation purposes

    @validates('status') # name of field to validate
    def validate_status(self, value):
        # If trying to set this card to 'Ongoing' ...
        if value == VALID_STATUSES[2]:
            stmt = db.select(db.func.count()).select_from(Card).filter_by(status=VALID_STATUSES[2])
            count = db.session.scalar(stmt)
            # ... and there's already an ongoing card in the database
            if count > 0:
                raise ValidationError('You already have an ongoing card')


    class Meta:
        fields = ('id', 'title', 'description', 'status', 'priority', 'date', 'user', 'comments')
        ordered = True
