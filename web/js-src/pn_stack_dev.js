/*
 * React components 
 */
var Article = React.createClass({
  render: function() {
    var itemClasses = classNames("col-md-12 item", 
                                {'item-first': this.props.count==1});
    var domain = pn_stack.extractDomain(this.props.article.url);
    var linkId = "link_"+ this.props.article.id;
    return (
      <div className="row row-no-margin">
        <div className={itemClasses}>
          <div className="inline item-number">{this.props.count}.</div>
          <div className="inline item-content">
            <p>
              <a className="item-link" id={linkId} href={this.props.article.url}>{this.props.article.title}</a> 
              <span className="item-domain">- {domain}</span>
            </p>
          </div>
        </div>
      </div>
    );
  }
});

var Articles = React.createClass({
  render: function() {
    var count = 1;
    var articles = this.props.articles.map(function(article) {
        return (
          <Article key={article.id} count={count++} article={article} />
        );
      });

    return ( 
      <div className="container">
        {articles}
      </div>  
    );
  }
});


/* 
 * Application logic
 */
var pn_stack = {
  articles: null,
  userVector: null,

  /* Initialize everything */
  init: function() {
    if(typeof(Storage) === "undefined") {
      alert("No web storage", "Your browser does not support web storage");
      throw new Error("No web storage");
    }

    if (!localStorage.userVector)
      this.makeNewUserVector();
    else
      this.userVector = JSON.parse(localStorage.userVector);

    this.getArticles();
  },

  /* User vector manipulation */
  // Create and save new user vector
  makeNewUserVector: function() {
    var vector = [];
    var normalizedSum = 0;

    while (normalizedSum != 1) { 
      normalizedSum = 0;
      initialSum = 0;

      vector = this.vectorRand(1000);
      sum = this.vectorSum(vector);
      vector = this.vectorDiv(vector, sum);

      normalizedSum = this.vectorSum(vector);
    }

    this.userVector = vector;
    localStorage.userVector = JSON.stringify(vector);
  },

  // Update user vector with latest article
  updateUserVector: function(article) {
    var userVector = this.userVector;
    var articleVector = article.article_vector;

    var newVector = this.vectorAdd(userVector, articleVector);
    sum = this.vectorSum(newVector);
    newVector = this.vectorDiv(newVector, sum);

    this.userVector = newVector;
    localStorage.userVector = JSON.stringify(newVector);

    this.renderArticles();
  },

  // Reset/create new random user vector
  resetUserVector: function() {
    this.makeNewUserVector();
    this.renderArticles();
  },

  /* Article manipulation */
  // Get and sanitize data
  getArticles: function() {
    this_ = this;

    $.getJSON("data/top_articles.json", function(rawArticles) {
      this_.articles = rawArticles.map(function(article) {
        return {id: article.id,
                url: this_.escapeHtml(article.url),
                title: this_.escapeHtml(article.title),
                article_vector: article.article_vector[0],
                cosDist: -1}
      }); 

      this_.renderArticles();
    });
  },

  // Calculate and order list. Render list with React.
  renderArticles: function() {
    this_ = this;
    var articles = this.articles;
    var userVector = this.userVector;
    
    articles.forEach(function(article) {
      article.cosDist = this_.vectorDot(article.article_vector, userVector);
    });

    articles.sort(function(a, b) {
      if (a.cosDist > b.cosDist) return -1;
      else if (a.cosDist < b.cosDist) return 1;
      else return 0;
    });

    React.render(
      <Articles articles={articles} />,
      document.getElementById("items")
    );

    this.registerClickHandler();
  },

  //
  updateArticles: function(article) {
    console.log("Update and send", article);
  },

  // Return article with article_id
  getArticle: function(article_id) {
    var articles = this.articles;
    var ret = null;
    
    articles.forEach(function(article) {
      if (article.id == article_id) {
        ret = article;
        return false;
      }

      return true;
    });
    
    return ret;
  },

  /* Handle article link clicks */
  registerClickHandler: function(link_id) {
    this_ = this;
    
    $(".item-link").mousedown(function(event) {
      if (event.which == 1 || event.which == 3) {
        var article_id = parseInt(event.target.id.substring(5));
        var article = this_.getArticle(article_id);
        this_.updateUserVector(article);
        this_.updateArticles(article);
      }
    });
  },

  /* Util */
  // Generates a n-dim (uniform-)random vector
  vectorRand: function(n) {
    var vector = [];
    for (var i = 0; i < n; i++)
      vector.push(Math.random());

    return vector;
  },

  // Vector scalar product
  vectorDot: function(a, b) {
    if (a.length != b.length)
      throw new Error("Vector length missmatch");

    var sum = 0;
    for (var i = 0; i < a.length; i++)
      sum += a[i]*b[i];

    return sum;
  },

  // Vector addition
  vectorAdd: function(a, b) {
     if (a.length != b.length)
      throw new Error("Vector length missmatch");

    var result = [];
    for (var i = 0; i < a.length; i++)
      result.push(a[i]+b[i]);

    return result;
  },

  // Sum of all elements
  vectorSum: function(vector) {
    var sum = 0;
    vector.forEach(function(x_i) {
      sum += x_i;
    });

    return sum;
  },

  // Vector division by scalar
  vectorDiv: function(vector, scalar) {
    var result = [];
    vector.forEach(function(x_i) {
      result.push(x_i/scalar);
    });

    return result;
  },

  // Use the browser's built-in functionality to quickly 
  // and safely escape the string
  escapeHtml: function(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  },

  // Extract the domain from an url
  extractDomain: function(url) {
    var domain;

    if (url.indexOf("://") > -1)
        domain = url.split('/')[2];
    else 
        domain = url.split('/')[0];
    
    domain = domain.split(':')[0];
    
    return domain;
  }
}

pn_stack.init();