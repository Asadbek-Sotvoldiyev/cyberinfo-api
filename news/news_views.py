class NewViews:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('views')

        if 'views' not in request.session:
            cart = self.session['views'] = {}
        self.cart = cart

    def add(self, article):
        article_id = str(article.id)
        if article_id not in self.cart:
            self.cart[article_id] = str(article.views)
            article.views += 1
            article.save()

        self.session.modified = True
