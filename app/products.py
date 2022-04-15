from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms import DecimalField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Optional
from flask_login import current_user
from .utils import s3_upload_small_files

import copy

from .models.product import Product

bp = Blueprint('products', __name__, url_prefix='/products')


def getSharedData():
    myProducts = Product.get_all_products_from_user(current_user.id)
    create_product_form = CreateProductForm()
    update_product_form = UpdateProductForm()
    update_product_form.pid.choices = list(map(lambda x: (x.id, x.id), myProducts))
    return (myProducts, create_product_form, update_product_form)


class CreateProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = DecimalField('Price', validators=[InputRequired(), NumberRange(min=0)], places=2)
    category = SelectField('Category', choices=['Food', 'Clothing', 'Pet Supplies', 'Health & Beauty', 'Home', 'Electronics', 'Entertainment', 'Other'], default=1)
    description = StringField('Description', validators=[DataRequired()])
    image = FileField('Image', validators=[FileRequired(), FileAllowed(["png", "jpg", "jpeg"], "This file is not a valid image!",)])
    submit = SubmitField('Create Product')


class UpdateProductForm(FlaskForm):
    pid = SelectField('Product ID', validators=[DataRequired()])
    name = StringField('New Name (Optional)')
    price = DecimalField('New Price (Optional)', validators=[Optional(), NumberRange(min=0)], places=2)
    category = SelectField('New Category (Optional)', choices=['', 'Food', 'Clothing', 'Pet Supplies', 'Health & Beauty', 'Home', 'Electronics', 'Entertainment', 'Other'], default=1)
    description = StringField('New Description (Optional)')
    image = FileField('New Image (Optional)', validators=[FileAllowed(["png", "jpg", "jpeg"], "This file is not a valid image!",)])
    submit = SubmitField('Update Product')


@bp.route('/')
def index():
    (myProducts, create_product_form, update_product_form) = getSharedData()
    return render_template('my_products.html',
        myProducts=myProducts,
        create_product_form=create_product_form,
        update_product_form=update_product_form)


@bp.route('/create', methods=['POST'])
def create():
    (myProducts, create_product_form, update_product_form) = getSharedData()
    if request.method == 'POST' and create_product_form.validate_on_submit():
        response = upload_files_to_s3(create_product_form.image)
        if response[0]:
            image_url = response[1]
            if Product.create_product(create_product_form.name.data, round(create_product_form.price.data, 2), create_product_form.category.data, create_product_form.description.data, image_url, current_user.id) == 0:
                flash("Product name already taken!")
            else:
                flash("Product successfully created!")
                return redirect(url_for('products.index'))
        else:
            flash("File upload unsuccessful")
    return render_template('my_products.html',
        myProducts=myProducts,
        create_product_form=create_product_form,
        update_product_form=update_product_form)


@bp.route('/update', methods=['POST'])
def update():
    (myProducts, create_product_form, update_product_form) = getSharedData()
    if request.method == 'POST' and update_product_form.validate_on_submit():
        currProduct = next(product for product in myProducts if str(product.id) == str(update_product_form.pid.data))
        currProduct = copy.deepcopy(currProduct)
        if update_product_form.name.data:
            currProduct.name = update_product_form.name.data
        if update_product_form.price.data:
            currProduct.price = update_product_form.price.data
        if update_product_form.category.data:
            currProduct.category = update_product_form.category.data    
        if update_product_form.description.data:
            currProduct.description = update_product_form.description.data
        if update_product_form.image.has_file():
            response = upload_files_to_s3(update_product_form.image)
            if response[0]:
                currProduct.image_url = response[1]
            else:
                flash("File upload unsuccessful")
                return render_template('my_products.html', 
                    myProducts=myProducts, 
                    create_product_form=create_product_form, 
                    update_product_form=update_product_form)
        update_result = Product.update_product(update_product_form.pid.data,
            currProduct.name, currProduct.price, currProduct.category, currProduct.description, currProduct.image_url)
        if update_result == 1:
            return redirect(url_for('products.index'))
        else:
            flash(update_result)
    return render_template('my_products.html', 
        myProducts=myProducts, 
        create_product_form=create_product_form, 
        update_product_form=update_product_form)


def upload_files_to_s3(file):
        file_to_upload = file.data
        content_type = file_to_upload.mimetype
        if file_to_upload.filename == '':
            flash(' *** No files Selected', 'danger')
        if file_to_upload:
            file_name = secure_filename(file_to_upload.filename)
            bucket_name = "mini-amazon-databaes"
            res = s3_upload_small_files(file_to_upload, bucket_name, file_name, content_type)
            if res['ResponseMetadata']['HTTPStatusCode']:
                return True, f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
            else:
                return False, None
        else:
            flash(f'File not found', 'danger')
