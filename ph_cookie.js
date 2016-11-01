var page = require('webpage').create();
url = 'http://searchdns.netcraft.com/?restriction=site+contains&host=wuyun.org&lookup=wait..&position=limited'
page.open(url, function(status) {
  var cookie = page.evaluate(function() {
    return document.cookie;
  });
  console.log(cookie);
  phantom.exit();
});