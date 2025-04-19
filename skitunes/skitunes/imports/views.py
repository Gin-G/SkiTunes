# Add these imports to the existing imports in your views.py file
from flask import request, render_template, redirect, url_for, flash, send_file
from skitunes import app, db
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional
from wtforms import SubmitField
import pandas as pd
import csv
import io
from flask_login import login_required, current_user
from skitunes.spotify.models import ski_movie_song_info, Movie

# Form for CSV upload
class CSVUploadForm(FlaskForm):
    csv_file = FileField('CSV File', validators=[
        FileAllowed(['csv'], 'CSV files only!')
    ])
    submit = SubmitField('Upload and Process')

# Form for manual entry
class ManualEntryForm(FlaskForm):
    song_name = StringField('Song Name', validators=[DataRequired()])
    song_artist = StringField('Artist', validators=[DataRequired()])
    song_album = StringField('Album', validators=[Optional()])
    song_num = StringField('Song Number', validators=[Optional()])
    genres = StringField('Genres', validators=[Optional()])
    spotify_id = StringField('Spotify Link', validators=[Optional()])
    skier_name = StringField('Skier Name(s)', validators=[Optional()])
    movie_name = StringField('Movie Name', validators=[DataRequired()])
    movie_year = StringField('Movie Year', validators=[DataRequired()])
    movie_co = StringField('Production Company', validators=[DataRequired()])
    ski_type = StringField('Primary Ski Style', validators=[Optional()])
    location = StringField('Location', validators=[Optional()])
    video_link = StringField('Video Link', validators=[Optional()])
    submit = SubmitField('Add Entry')

# Routes for bulk import options
@app.route('/skitunes/bulk_import', methods=['GET'])
@login_required
def bulk_import_view():
    # Check if current user is admin
    if current_user.email not in ['nickco7@gmail.com', 'sgmorgan16@gmail.com','ncote@ucar.edu']:
        flash('Unauthorized access')
        return redirect(url_for('home'))
        
    upload_form = CSVUploadForm()
    manual_form = ManualEntryForm()
    return render_template('bulk_import.html', upload_form=upload_form, manual_form=manual_form)

# Route to download CSV template
@app.route('/skitunes/download_csv_template', methods=['GET'])
@login_required
def download_csv_template():
    # Check if current user is admin
    if current_user.email not in ['nickco7@gmail.com', 'sgmorgan16@gmail.com', 'ncote@ucar.edu']:
        flash('Unauthorized access')
        return redirect(url_for('home'))
        
    # Create a CSV template with all required fields
    fields = [
        "Song Name", "Artist", "Song Album", "Song Number", 
        "Genres", "Spotify Link", "Skier Name(s)", 
        "Skiing type", "Location", "Movie Name", 
        "Movie Year", "Production Co."
    ]
    
    # Create a buffer for the CSV
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(fields)
    
    # Add an example row for format reference
    example_row = [
        "Example Song", "Example Artist", "Example Album", "1",
        "['Rock', 'Pop']", "https://open.spotify.com/track/123456", "John Doe",
        "Freestyle", "Colorado", "Ski Movie 2023",
        "2023", "Ski Productions"
    ]
    writer.writerow(example_row)
    
    # Prepare the response
    buffer.seek(0)
    return send_file(
        io.BytesIO(buffer.getvalue().encode('utf-8')),
        mimetype='text/csv',
        download_name='ski_movie_template.csv',
        as_attachment=True
    )

# Route to handle CSV upload and processing
@app.route('/skitunes/process_csv_upload', methods=['POST'])
@login_required
def process_csv_upload():
    # Check if current user is admin
    if current_user.email not in ['nickco7@gmail.com', 'sgmorgan16@gmail.com', 'ncote@ucar.edu']:
        flash('Unauthorized access')
        return redirect(url_for('home'))
        
    form = CSVUploadForm()
    
    if not form.validate_on_submit():
        flash('Invalid form submission')
        return redirect(url_for('bulk_import_view'))
    
    if not form.csv_file.data:
        flash('No file uploaded')
        return redirect(url_for('bulk_import_view'))
    
    # Read the CSV file
    try:
        csv_file = form.csv_file.data
        # Convert to a list of dictionaries that can be processed
        csv_data = pd.read_csv(csv_file)
        records = csv_data.to_dict('records')
        
        # Process the records
        success_count, duplicate_count, total_entries = process_bulk_records(records)
        
        flash(f'CSV Import completed: {success_count} entries added, {duplicate_count} duplicates skipped')
        return redirect(url_for('home'))
        
    except Exception as e:
        flash(f'Error processing CSV file: {str(e)}')
        return redirect(url_for('bulk_import_view'))

# Route to handle manual entry form
@app.route('/skitunes/process_manual_entry', methods=['POST'])
@login_required
def process_manual_entry():
    # Check if current user is admin
    if current_user.email not in ['nickco7@gmail.com', 'sgmorgan16@gmail.com', 'ncote@ucar.edu']:
        flash('Unauthorized access')
        return redirect(url_for('home'))
        
    form = ManualEntryForm()
    
    if form.validate_on_submit():
        # Create a dictionary from form data
        record = {
            "Song Name": form.song_name.data,
            "Artist": form.song_artist.data,
            "Song Album": form.song_album.data or "Unknown",
            "Song Number": form.song_num.data or "Unknown",
            "Genres": form.genres.data or "Unknown",
            "Spotify Link": form.spotify_id.data or "Not Found",
            "Skier Name(s)": form.skier_name.data or "Unknown",
            "Skiing type": form.ski_type.data or "Unknown",
            "Location": form.location.data or "Unknown",
            "Movie Name": form.movie_name.data,
            "Movie Year": form.movie_year.data,
            "Production Co.": form.movie_co.data,
            "Video Link": form.video_link.data or "Unknown"
        }
        
        # Check for duplicate entries
        existing_entry = check_duplicate_entry(record)
        
        if existing_entry:
            flash('This song already exists for this artist in this movie')
            return redirect(url_for('bulk_import_view'))
        
        try:
            # Create movie record
            movie = Movie(
                movie_name=record["Movie Name"],
                movie_year=record["Movie Year"],
                movie_co=record["Production Co."],
                movie_img_url='None'
            )
            
            # Create song info record
            movie_song_info = ski_movie_song_info(
                song_name=record["Song Name"],
                song_artist=record["Artist"],
                song_album=record["Song Album"],
                song_num=record["Song Number"],
                genres=record["Genres"],
                spotify_id=record["Spotify Link"],
                skier_name=record["Skier Name(s)"],
                ski_type=record["Skiing type"],
                location=record["Location"],
                video_link=record["Video Link"]
            )
            
            movie_song_info.movie_details.append(movie)
            db.session.add(movie_song_info)
            db.session.commit()
            
            flash('Entry successfully added to the database')
            return redirect(url_for('bulk_import_view'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding entry: {str(e)}')
            return redirect(url_for('bulk_import_view'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}")
        return redirect(url_for('bulk_import_view'))

# Function to process bulk records (can be used by both CSV and JSON imports)
def process_bulk_records(records):
    success_count = 0
    duplicate_count = 0
    total_entries = len(records)
    
    print(f"Total entries to process: {total_entries}")
    
    for record in records:
        # Check if this is a duplicate entry
        existing_entry = check_duplicate_entry(record)
        
        if not existing_entry:
            # Create movie record
            movie = Movie(
                movie_name=record["Movie Name"],
                movie_year=str(record["Movie Year"]),  # Convert to string to handle year values
                movie_co=record["Production Co."],
                movie_img_url='None'
            )
            
            # Create song info record
            movie_song_info = ski_movie_song_info(
                song_name=record["Song Name"],
                song_artist=record["Artist"],
                song_album=record["Song Album"],
                song_num=str(record["Song Number"]),  # Convert to string
                genres=str(record["Genres"]) if "Genres" in record and record["Genres"] else "Unknown",
                spotify_id=record["Spotify Link"],
                skier_name=record["Skier Name(s)"],
                ski_type=record["Skiing type"],
                location=record["Location"],
                video_link='Unknown'
            )
            
            movie_song_info.movie_details.append(movie)
            db.session.add(movie_song_info)
            success_count += 1
        else:
            duplicate_count += 1
    
    # Commit all the changes at once
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error committing records: {str(e)}")
        raise e
    
    print(f"\nFinal counts:")
    print(f"Total entries processed: {total_entries}")
    print(f"Successful additions: {success_count}")
    print(f"Duplicates skipped: {duplicate_count}")
    
    return success_count, duplicate_count, total_entries

# Helper function to check for duplicate entries
def check_duplicate_entry(record):
    try:
        # First check for exact duplicate
        exact_duplicate = db.session.query(ski_movie_song_info)\
            .join(ski_movie_song_info.movie_details)\
            .filter(
                ski_movie_song_info.song_name == record["Song Name"],
                ski_movie_song_info.song_artist == record["Artist"],
                Movie.movie_name == record["Movie Name"],
                Movie.movie_year == str(record["Movie Year"])
            ).first()
            
        return exact_duplicate
    except Exception as e:
        print(f"Error checking for duplicate: {str(e)}")
        return None

