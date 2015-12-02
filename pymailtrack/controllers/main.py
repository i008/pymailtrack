from flask import (
    Blueprint, render_template, flash, request,
    redirect, url_for, send_file, jsonify, current_app
)
from flask.ext.login import (
    login_user, logout_user, login_required, current_user
)

import uuid
import datetime

from pymailtrack.extensions import cache
from pymailtrack.forms import LoginForm, TrackForm
from pymailtrack.models import User, Logs,TrackingCode, db

main = Blueprint('main', __name__)


@main.route('/')
@cache.cached(timeout=1000)
def home():
    return render_template('index.html')


@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user)

        flash("Logged in successfully.", "success")
        return redirect(request.args.get("next") or url_for(".home"))

    return render_template("login.html", form=form)


@main.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")

    return redirect(url_for(".home"))


@main.route("/restricted")
@login_required
def restricted():
    return "You can only see this if you are logged in!", 200


@main.route('/track/<trackhash>')
def tracking_image(trackhash):
    ip = request.remote_addr
    time = datetime.datetime.utcnow()
    code_id = TrackingCode.query.filter(TrackingCode.trackhash == trackhash).one().id
    l = Logs(ip=ip, code_id=code_id, time=time)
    db.session.add(l)
    db.session.commit()
    return send_file('tr.png')


@main.route('/generate_track', methods=["GET", "POST"])
@login_required
def generate_track():
    trackform = TrackForm()
    if trackform.validate_on_submit():
        trackhash = str(uuid.uuid4())[:7]

        tc = TrackingCode(
            description=trackform.description.data,
            recipient=trackform.recipient.data,
            trackhash=trackhash,
            user_id=current_user.id
        )

        db.session.add(tc)
        db.session.commit()
        track_url = current_app.config.get('BASE_SERVER_NAME') + url_for('.tracking_image', trackhash=trackhash)
        trackcode = "<img width='0' height='0' src={0}>".format(track_url)

        return render_template("gentrackform.html",form=trackform, trackcode=trackcode)

    return render_template("gentrackform.html", form=trackform, trackcode='')



@main.route('/yourtrack', methods=['GET'])
@login_required
def yourtrack():
    return render_template("yourtrack.html")



@main.route('/trackingcode')
def generate_tracking_code():
    unique_id = str(uuid.uuid4())[:7]
    track_url = current_app.config.get('BASE_SERVER_NAME') + url_for('.tracking_image', trackhash=unique_id)
    return jsonify(
        {'tracking_code':"<img width='0' height='0' src={0}>".format(track_url)}
    )

@main.route('/plg')
def playground():
    return current_app.config.get('BASE_SERVER_NAME')
