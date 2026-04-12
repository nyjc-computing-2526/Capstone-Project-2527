Hi @Vinc-ops since you're already fixing the route issues, could you also go through every file and refactor hardcoded auth "href"s and form "action"s into {{url_for("...")}} format? Tq

An example would be the /auth/logout to {{ url_for('auth.logout') }} for all pages