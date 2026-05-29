from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

# =============================================
# CONFIGURATION DE L'APPLICATION
# =============================================

app = Flask(__name__)

# Connexion à la base de données MySQL
# Format : mysql+pymysql://utilisateur:motdepasse@hote/nom_base
app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql+pymysql://sae23_user:123@localhost/sae23')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Désactive les avertissements inutiles
app.secret_key = 'change_this_in_production'           # Clé secrète pour les sessions Flask

db = SQLAlchemy(app)  # On lie SQLAlchemy à notre application Flask

# Identifiants de connexion admin
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"


# =============================================
# MODÈLES (représentent les tables de la BDD)
# =============================================

class Semestre(db.Model):
    """
    Table : semestre
    Exemple : S1 - Semestre 1
    """
    id    = db.Column(db.Integer, primary_key=True)   # Identifiant unique auto-incrémenté
    code  = db.Column(db.String(10), nullable=False)  # Ex : "S1"
    nom   = db.Column(db.String(100), nullable=False) # Ex : "Semestre 1"
    # Relation : un semestre contient plusieurs blocs
    blocs = db.relationship('Bloc', backref='semestre', lazy=True)


class Bloc(db.Model):
    """
    Table : bloc
    Exemple : B1-S1 - Administrer (dans le Semestre 1)
    """
    id          = db.Column(db.Integer, primary_key=True)
    code        = db.Column(db.String(10), nullable=False)   # Ex : "B1-S1"
    nom         = db.Column(db.String(100), nullable=False)  # Ex : "Administrer"
    semestre_id = db.Column(db.Integer, db.ForeignKey('semestre.id'), nullable=False)
    # Relation : un bloc contient plusieurs compétences
    competences = db.relationship('Competence', backref='bloc', lazy=True)


class Competence(db.Model):
    """
    Table : competence
    Exemple : AC11.01 - Maîtriser les lois fondamentales de l'électricité
    """
    id      = db.Column(db.Integer, primary_key=True)
    code    = db.Column(db.String(20), nullable=False)    # Ex : "AC11.01"
    nom     = db.Column(db.String(255), nullable=False)   # Nom complet
    # Niveau parmi 5 valeurs possibles, "non acquis" par défaut
    niveau  = db.Column(
        db.Enum('non acquis', 'en cours', 'presque acquis', 'acquis', 'expert'),
        default='non acquis'
    )
    bloc_id = db.Column(db.Integer, db.ForeignKey('bloc.id'), nullable=False)


# =============================================
# ROUTES — PAGES PUBLIQUES
# =============================================

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html', active='index')


@app.route('/cv')
def cv():
    """Page CV / Parcours"""
    return render_template('CV.html', active='cv')


@app.route('/portfolio')
def portfolio():
    """Page portfolio — liste des 5 compétences"""
    return render_template('portfolio.html', active='portfolio')


@app.route('/credits')
def credits():
    """Page crédits et mentions légales"""
    return render_template('credits.html')


# =============================================
# ROUTES — PAGES PORTFOLIO DÉTAIL
# =============================================

@app.route('/portfolio/administrer')
def portfolio_administrer():
    return render_template('portfolio-administrer.html', active='portfolio')


@app.route('/portfolio/connecter')
def portfolio_connecter():
    return render_template('portfolio-connecter.html', active='portfolio')


@app.route('/portfolio/programmer')
def portfolio_programmer():
    return render_template('portfolio-programmer.html', active='portfolio')


@app.route('/portfolio/surveiller')
def portfolio_surveiller():
    return render_template('portfolio-surveiller.html', active='portfolio')


@app.route('/portfolio/securiser')
def portfolio_securiser():
    return render_template('portfolio-securiser.html', active='portfolio')


# =============================================
# ROUTES — AUTHENTIFICATION
# =============================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET  → affiche le formulaire de connexion
    POST → vérifie les identifiants :
           - corrects → stocke la session et redirige vers /admin
           - incorrects → réaffiche le formulaire avec error=True
    """
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin'))
        return render_template('login.html', error=True)
    return render_template('login.html', error=False)



# =============================================
# ROUTES — ADMIN
# =============================================

@app.route('/admin')
def admin():
    if not session.get('admin'):             # si pas connecté → retour login
        return redirect(url_for('login'))
    semestres = Semestre.query.all()
    return render_template('admin.html', semestres=semestres)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))


@app.route('/admin/valider', methods=['POST'])
def valider():
    competence_id  = request.form.get('competence_id')
    nouveau_niveau = request.form.get('niveau')
    if competence_id and nouveau_niveau:
        comp = Competence.query.get(competence_id)
        if comp:
            comp.niveau = nouveau_niveau
            db.session.commit()
    return redirect(url_for('admin') + '?success=1')


# =============================================
# LANCEMENT
# =============================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
