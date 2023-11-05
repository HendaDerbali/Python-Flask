from flask import render_template,redirect,session,request, flash
from flask_app import app
from flask_app.models.thought import Thought
from flask_app.models.user import User



@app.route('/logout')
def logout():
        session.clear()
        return redirect('/')



@app.route('/add_thought',methods=['POST'])
def add_thought():
    if 'user_id' not in session:
        return redirect('/logout')
    if not Thought.validate_thought(request.form):
        return redirect('/thoughts')
    data = {
        "post": request.form["post"],
        "user_id": session["user_id"]
    }
    Thought.save(data)
    return redirect('/thoughts')



@app.route('/users/<int:user_id>')
def show_thoughts(user_id):
    if 'user_id' in session :
        logged_user = User.get_by_id({'id' : session['user_id']})

        user = User.get_by_id({'id' : user_id})
        if user : 
            user_posts = Thought.get_user_posts({'user_id': user_id})
            return render_template('user_page.html',user=user,user_posts=user_posts,logged_user=logged_user)
        else :
            return redirect('/thoughts')
    
    return redirect('/')



@app.route('/users/<int:id>')
def show(id):
    thought = Thought.get_by_id({'id': id})
    return render_template('user_page.html', thought = thought)



@app.route('/thoughts')
def dashboard():
    if not 'user_id' in session:
        return redirect('/')
    
    logged_user = User.get_by_id({'id' : session['user_id']})

    result = Thought.get_all()
    return render_template("dashboard.html", logged_user = logged_user, thoughts = result)


@app.route('/thoughts/<int:id>/delete')
def delete(id):
    result = Thought.delete({'id': id})
    return redirect('/thoughts')




@app.route('/thoughts/<int:id>/favorite')
def favorite(id):
    user_id = session['user_id']
    data = {
        'thought_id': id,
        'user_id': user_id
    }
    Thought.favorite(data)
    return redirect('/thoughts')

@app.route('/thoughts/<int:id>/unfavorite')
def unfavorite(id):
    user_id = session['user_id']
    data = {
        'thought_id': id,
        'user_id': user_id
    }
    Thought.unfavorite(data)
    return redirect('/thoughts')


