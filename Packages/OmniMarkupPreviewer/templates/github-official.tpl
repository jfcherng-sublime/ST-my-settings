%# ---------------------------------- WARNING ----------------------------------
%#       Do NOT Modify this template, create a new one for customization
%#                It will get overwritten upon update
%# -----------------------------------------------------------------------------
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{{filename}} @ {{dirname}}</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
    <link rel="stylesheet" href="/public/github-official/framework.css">
    <link rel="stylesheet" href="/public/github-official/github.css">
    <link rel="stylesheet" href="/public/github-official/admonition.css">
    <link rel="stylesheet" href="/public/github-official/codehilite.css">
    <link rel="stylesheet" href="/public/github-official/my.css">
  </head>
  <body>
    <div class="container">
      <div class="repository-content">
        <div class="boxed-group"><!-- just for top margin --></div>
        <div id="markup" class="readme boxed-group clearfix">
          <h3>
            <svg class="octicon octicon-file" viewBox="0 0 12 16" version="1.1" width="12" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M6 5H2V4h4v1zM2 8h7V7H2v1zm0 2h7V9H2v1zm0 2h7v-1H2v1zm10-7.5V14c0 .55-.45 1-1 1H1c-.55 0-1-.45-1-1V2c0-.55.45-1 1-1h7.5L12 4.5zM11 5L8 2H1v12h10V5z"></path></svg>
            <span class="file-title">{{filename}} @ {{dirname}}</span>
          </h3>
          <article id="content" class="markdown-body">
            {{!html_part}}
          </article>
        </div>
      </div>
    </div>
  </body>
  <script type="text/x-omnimarkup-config">
    window.App.Context = {
      buffer_id: {{buffer_id}},
      timestamp: '{{timestamp}}',
      revivable_key: '{{revivable_key}}'
    };
    window.App.Options = {
      ajax_polling_interval: {{ajax_polling_interval}},
      mathjax_enabled: {{'true' if mathjax_enabled else 'false'}}
    };
  </script>
  <script type="text/javascript" src="/public/jquery-3.3.1.min.js"></script>
  <script type="text/javascript" src="/public/imagesloaded.pkgd.min.js"></script>
  <script type="text/javascript" src="/public/app.js"></script>
  %if mathjax_enabled:
  <script type="text/x-mathjax-config">
    MathJax.Hub.Config({
        tex2jax: {
          inlineMath: [ ['$','$'], ["\\(","\\)"] ],
          displayMath: [ ['$$', '$$'], ["\\[", "\\]"] ],
          processEscapes: true
        },
        TeX: {
          equationNumbers: {
            autoNumber: 'AMS'
          }
        },
        'HTML-CSS': {
          imageFont: null
        }
      });
  </script>
  <script type="text/javascript" src="/public/mathjax/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
  %end
</html>
