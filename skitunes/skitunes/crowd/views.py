from flask import redirect, url_for, flash, render_template, request
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from skitunes import app, db
from skitunes.spotify.models import Movie, ski_movie_song_info
from skitunes.crowd.models import PendingEntry, EntryVote, APPROVAL_THRESHOLD
from skitunes.crowd.forms import SuggestEntryForm, ActionForm

ADMIN_EMAILS = {'nickco7@gmail.com', 'sgmorgan16@gmail.com'}


def _promote_entry(entry):
    movie = Movie(
        movie_name=entry.movie_name,
        movie_year=entry.movie_year,
        movie_co=entry.movie_co,
        movie_img_url='None'
    )
    song = ski_movie_song_info(
        song_name=entry.song_name,
        song_artist=entry.song_artist or '',
        song_album=entry.song_album or '',
        song_num=entry.song_num or '',
        genres=entry.genres or '',
        spotify_id=entry.spotify_id or 'Not Found',
        skier_name=entry.skier_name or '',
        ski_type=entry.ski_type or '',
        location=entry.location or '',
        video_link=entry.video_link or 'Unknown'
    )
    song.movie = movie
    db.session.add(song)
    db.session.delete(entry)
    db.session.commit()


@app.route('/skitunes/suggest', methods=['GET', 'POST'])
@login_required
def suggest_entry():
    form = SuggestEntryForm()
    if form.validate_on_submit():
        entry = PendingEntry(
            song_name=form.song_name.data,
            song_artist=form.song_artist.data,
            song_album=form.song_album.data,
            song_num=form.song_num.data,
            genres=form.genres.data,
            spotify_id=form.spotify_id.data,
            skier_name=form.skier_name.data,
            ski_type=form.ski_type.data,
            location=form.location.data,
            video_link=form.video_link.data,
            movie_name=form.movie_name.data,
            movie_year=form.movie_year.data,
            movie_co=form.movie_co.data,
            submitted_by=current_user.user_id
        )
        db.session.add(entry)
        db.session.commit()
        flash('Entry submitted! It will appear in the live database once 5 users confirm it.')
        return redirect(url_for('pending_entries'))
    return render_template('suggest.html', suggest_form=form)


@app.route('/skitunes/pending')
@login_required
def pending_entries():
    entries = PendingEntry.query.order_by(PendingEntry.submitted_at.desc()).all()
    user_has_voted = {}
    is_submitter = {}
    for entry in entries:
        is_submitter[entry.id] = (entry.submitted_by == current_user.user_id)
        user_has_voted[entry.id] = any(
            v.user_id == current_user.user_id for v in entry.votes
        )
    action_form = ActionForm()
    return render_template(
        'pending.html',
        entries=entries,
        user_has_voted=user_has_voted,
        is_submitter=is_submitter,
        action_form=action_form,
        admin_emails=ADMIN_EMAILS,
        threshold=APPROVAL_THRESHOLD
    )


@app.route('/skitunes/pending/<int:entry_id>/vote', methods=['POST'])
@login_required
def vote_entry(entry_id):
    entry = PendingEntry.query.get_or_404(entry_id)
    if entry.submitted_by == current_user.user_id:
        flash('You cannot confirm your own submission.')
        return redirect(url_for('pending_entries'))
    already_voted = any(v.user_id == current_user.user_id for v in entry.votes)
    if already_voted:
        flash('You have already confirmed this entry.')
        return redirect(url_for('pending_entries'))
    vote = EntryVote(pending_entry_id=entry_id, user_id=current_user.user_id)
    db.session.add(vote)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('You have already confirmed this entry.')
        return redirect(url_for('pending_entries'))
    db.session.refresh(entry)
    if len(entry.votes) >= APPROVAL_THRESHOLD:
        _promote_entry(entry)
        flash('Entry auto-approved and added to the database!')
    else:
        flash(f'Confirmation recorded ({len(entry.votes)}/{APPROVAL_THRESHOLD})')
    return redirect(url_for('pending_entries'))


@app.route('/skitunes/pending/<int:entry_id>/approve', methods=['POST'])
@login_required
def approve_entry(entry_id):
    if current_user.email not in ADMIN_EMAILS:
        flash('Unauthorized access.')
        return redirect(url_for('home'))
    entry = PendingEntry.query.get_or_404(entry_id)
    _promote_entry(entry)
    flash('Entry approved and added to the database.')
    return redirect(url_for('pending_entries'))


@app.route('/skitunes/pending/<int:entry_id>/reject', methods=['POST'])
@login_required
def reject_entry(entry_id):
    if current_user.email not in ADMIN_EMAILS:
        flash('Unauthorized access.')
        return redirect(url_for('home'))
    entry = PendingEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('Entry rejected and deleted.')
    return redirect(url_for('pending_entries'))
