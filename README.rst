======================================================================
 pocket2pinboard -- Import articles saved via pocket into pinboard.in
======================================================================

pocket2pinboard copies your tagged articles from pocket to bookmarks
on pinboard.in.

Pinboard Authentication
=======================

pocket2pinboard uses the API token to access your pinboard account, so
it never needs your password.  Create a ``~/.pocket2pinboardrc`` file
containing your pinboard API token (available from
https://pinboard.in/settings/password).

::

  [pinboard]
  token = TOKEN_GOES_HERE

Pocket Authentication
=====================

pocket2pinboard authenticates with Pocket via their oauth broker.  `A
browser window is opened`_ to ask for read-only access to your Pocket
account, and after you grant access processing continues. If you have
already granted access and are already logged in to Pocket, the window
will close automatically without any intervention.

.. _A browser window is opened: https://docs.python.org/2/library/webbrowser.html
