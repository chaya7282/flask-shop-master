from operator import or_
from functools import reduce

from flask_login import UserMixin
from libgravatar import Gravatar
from sqlalchemy.ext.hybrid import hybrid_property

from flaskshop.database import Column, Model, db
from flaskshop.extensions import bcrypt
from flaskshop.constant import Permission
from flaskshop.resources.resources import get_presigned_url

class User(Model, UserMixin):
    __tablename__ = "account_user"
    username = Column(db.String(80), unique=True, nullable=False, comment="user`s name")
    email = Column(db.String(80), unique=True, nullable=False)
    #: The hashed password
    _password = Column("password", db.String(128))
    nick_name = Column(db.String(255))
    is_active = Column(db.Boolean(), default=False)
    open_id = Column(db.String(80), index=True)
    session_key = Column(db.String(80), index=True)
    contact_phone = Column(db.String(80),nullable=False)

    def __init__(self, username, email, password, **kwargs):
        super().__init__(username=username, email=email, password=password, **kwargs)

    def __str__(self):
        return self.username

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = bcrypt.generate_password_hash(value)

    @property
    def avatar(self):
        return Gravatar(self.email).get_image()

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    @property
    def addresses(self):
        return UserAddress.query.filter_by(user_id=self.id).first()


    @property
    def addresses_id(self):
        adresses = UserAddress.query.filter_by(user_id=self.id).first()
        if adresses:
            return adresses.id
        else:
            return None

    @property
    def is_active_human(self):
        return "Y" if self.is_active else "N"

    @property
    def roles(self):
        at_ids = (
            UserRole.query.with_entities(UserRole.role_id)
            .filter_by(user_id=self.id)
            .all()
        )
        return Role.query.filter(Role.id.in_(id for id, in at_ids)).all()


    def add_a_role(self, role_id):
        res= UserRole.query.filter_by(role_id=role_id, user_id=self.id).first()
        if not res:
            UserRole.create(user_id=self.id, role_id=role_id)
        return

    def delete(self):
        if self.addresses:
            self.addresses.delete()
        return super().delete()

    def can(self, permissions):
        if not self.roles:
            return False
        all_perms = reduce(or_, map(lambda x: x.permissions, self.roles))
        return all_perms & permissions == permissions

    def can_admin(self):
        return self.can(Permission.ADMINISTER)

    def can_edit(self):
        return self.can(Permission.EDITOR)


class Business(Model):
    __tablename__ = "business_details"
    address = Column(db.String(255), nullable=False)
    phone = Column(db.String(20), nullable=False)
    name= Column(db.String(80), unique=True)
    email = Column(db.String(80), nullable=True)
    email_password= Column(db.String(80), nullable=True)
    image= Column(db.String(255), nullable=True, default=None)
    account_sid  = Column(db.String(20), nullable=True)
    auth_token=Column(db.String(20), nullable=True)
    payPal_SID=Column(db.String(100), nullable=True)
    payPal_Secret = Column(db.String(100), nullable=True)
    Twilo_phone_Number=Column(db.String(20), nullable=True)
    def __str__(self):
        return self.name

    def get_image(self):
        url = None
        if self.image:
            url = get_presigned_url(self.image)
        return url


class UserAddress(Model):
    __tablename__ = "account_address"
    user_id = Column(db.Integer())
    province = Column(db.String(255),nullable=True)
    city = Column(db.String(255),nullable=True)
    district = Column(db.String(255),nullable=True)
    address = Column(db.String(255),nullable=False)
    contact_name = Column(db.String(255),nullable=False)
    contact_phone = Column(db.String(80),nullable=False)
    pincode = Column(db.String(80),nullable=True)
    email = Column(db.String(80),nullable=True)

    @property
    def full_address(self):
        return f"{self.contact_name}</br> {self.city}<br>{self.address}<br>{self.contact_phone}<br>"

    @hybrid_property
    def user(self):
        return User.get_by_id(self.user_id)

    def __str__(self):
        return self.full_address







class Role(Model):
    __tablename__ = "account_role"
    name = Column(db.String(80), unique=True)
    permissions = Column(db.Integer(), default=Permission.LOGIN)


class UserRole(Model):
    __tablename__ = "account_user_role"
    user_id = Column(db.Integer())
    role_id = Column(db.Integer())
