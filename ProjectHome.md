This is the smallest working example I could quickly make of an appengine application that does full CRUD. (It also attempts to use SearchableModel to make the results full-text searchable, but the SearchableModel code fails to update the index after the initial create due to a well-known bug). It has an example of using an inherited template, and uses the webapp framework.

It would be great to see some more documentation in the source files themselves, but most folks should be able to change the application name in app.yaml and GO.

If you really want to see it in action, it's running at http://pyx.appspot.com