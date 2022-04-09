from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms import DecimalField, StringField, SubmitField
from wtforms.validators import DataRequired, InputRequired, NumberRange
import time
from .utils import s3_upload_small_files

from .models.product import Product

bp = Blueprint('products', __name__, url_prefix='/products')

class CreateProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = DecimalField('Price', validators=[InputRequired(), NumberRange(min=0)], places=2)
    image = FileField('Image', validators=[FileRequired(), FileAllowed(["png", "jpg", "jpeg"], "This file is not a valid image!",)])
    submit = SubmitField('Create Product')

@bp.route('/create', methods=['GET', 'POST'])
def create():
    create_product_form = CreateProductForm()
    if request.method == 'POST' and create_product_form.validate_on_submit():
        response = upload_files_to_s3(create_product_form.image)
        if response[0]:
            image_url = response[1]
            if Product.create_product(create_product_form.name.data, round(create_product_form.price.data, 2), True, image_url) == 0:
                flash("Product name already taken!")
            else:
                flash("Product successfully created!")
                return redirect(url_for('products.create'))
        else:
            flash("File upload unsuccessful")

    return render_template('create_product.html', create_product_form=create_product_form)

def upload_files_to_s3(file):
        file_to_upload = file.data
        content_type = file_to_upload.mimetype
        # if empty files
        if file_to_upload.filename == '':
            flash(f' *** No files Selected', 'danger')
 
        if file_to_upload:
            file_name = secure_filename(file_to_upload.filename)
            bucket_name = "mini-amazon-databaes"
            region = "us-east-2"
            res = s3_upload_small_files(file_to_upload, bucket_name, file_name, content_type)
            if res['ResponseMetadata']['HTTPStatusCode']:
                return True, f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
            else:
                return False, None
        else:
            flash(f'File not found', 'danger')