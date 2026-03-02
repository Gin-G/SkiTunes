from datetime import datetime
from sqlalchemy import UniqueConstraint
from skitunes import db

APPROVAL_THRESHOLD = 5


class PendingEntry(db.Model):
    __tablename__ = 'pending_entries'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Song fields
    song_name = db.Column(db.String(200), nullable=False)
    song_artist = db.Column(db.String(200))
    song_album = db.Column(db.String(200))
    song_num = db.Column(db.String(50))
    genres = db.Column(db.String(500))
    spotify_id = db.Column(db.String(500))
    skier_name = db.Column(db.String(500))
    ski_type = db.Column(db.String(200))
    location = db.Column(db.String(500))
    video_link = db.Column(db.String(500))

    # Movie fields (denormalized)
    movie_name = db.Column(db.String(200), nullable=False)
    movie_year = db.Column(db.String(10))
    movie_co = db.Column(db.String(200))

    # Metadata
    submitted_by = db.Column(db.String(100), db.ForeignKey('Users.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    votes = db.relationship('EntryVote', back_populates='entry', cascade='all, delete-orphan')
    submitter = db.relationship('User', foreign_keys=[submitted_by])


class EntryVote(db.Model):
    __tablename__ = 'entry_votes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pending_entry_id = db.Column(db.Integer, db.ForeignKey('pending_entries.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(100), db.ForeignKey('Users.id'), nullable=False)
    voted_at = db.Column(db.DateTime, default=datetime.utcnow)

    entry = db.relationship('PendingEntry', back_populates='votes')
    voter = db.relationship('User', foreign_keys=[user_id])

    __table_args__ = (UniqueConstraint('pending_entry_id', 'user_id', name='uq_vote_per_user'),)
