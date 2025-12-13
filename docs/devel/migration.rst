.. _migration-guide:

Migrating to Weblate
====================

Are you using a different localization platform and considering switching to Weblate?
This guide provides a quick, step-by-step process to help you migrate your translation
project from platforms like Transifex, Crowdin, Lokalise, or similar services.

Weblate is designed around continuous localization with Git integration at its core,
making it ideal for teams that want to keep translations close to their development workflow.

.. seealso::

   * :doc:`starting` for choosing the right internationalization framework
   * :doc:`integration` for detailed integration options
   * :ref:`continuous-translation` for setting up automated workflows

Prerequisites
-------------

Before starting your migration, ensure you have:

**On your localization platform:**

* Access to export your translation files
* List of translators and their roles/permissions
* Understanding of your current workflow (review process, automation, etc.)

**For Weblate:**

* A Weblate instance (either `Hosted Weblate <https://hosted.weblate.org/>`_ or :doc:`self-hosted </admin/install>`)
* Your translation files stored in a Git repository (or other :ref:`VCS <vcs>`)
* Admin or project creation permissions on your Weblate instance

.. hint::

   If your translations are not yet in a Git repository, you can easily
   create one or use the :guilabel:`Upload translation files` option when
   creating a component.

Step 1: Prepare your translation files
---------------------------------------

Export translations from your current platform
+++++++++++++++++++++++++++++++++++++++++++++

Most localization platforms allow you to export all translations at once:

* **Transifex**: Use their CLI tool or download translations from the web interface
* **Crowdin**: Export all translations as a ZIP file from project settings
* **Lokalise**: Use the bulk export feature
* **Phrase**: Download all locales from the project dashboard

.. hint::

   Keep your translation files in the format native to your
   internationalization framework (PO, XLIFF, JSON, etc.) rather than
   converting them. Weblate supports :ref:`many formats <formats>`.

Commit translations to your Git repository
+++++++++++++++++++++++++++++++++++++++++++

If your translations aren't already in Git:

1. Create a Git repository or use your existing project repository
2. Organize translation files following your project structure
3. Commit and push the files to your Git hosting service (GitHub, GitLab, Bitbucket, etc.)

.. code-block:: shell

   git add locales/
   git commit -m "Add translation files for Weblate migration"
   git push origin main

.. seealso::

   * :ref:`continuous-translation` for optimal repository structure
   * :doc:`/vcs` for supported version control systems

Step 2: Import your project into Weblate
-----------------------------------------

Create a new project
++++++++++++++++++++

1. Navigate to your Weblate dashboard
2. Click :guilabel:`Add new translation project` (or use the **+** menu)
3. Fill in your project details:

   * **Project name**: Your application or project name
   * **URL slug**: Short identifier (e.g., ``myapp``)
   * **Project website**: Your project homepage (optional)

.. image:: /screenshots/user-add-project.webp

.. seealso::

   :ref:`adding-projects` for detailed project creation instructions

Add a component from your Git repository
+++++++++++++++++++++++++++++++++++++++++

1. After creating the project, click :guilabel:`Add new translation component`
2. Select :guilabel:`From version control`
3. Configure your component:

   * **Component name**: e.g., "Application strings", "Website", "Documentation"
   * **Repository URL**: Your Git repository URL (HTTPS or SSH)
   * **Repository branch**: Usually ``main`` or ``master``
   * **File mask**: Pattern matching your translation files (e.g., ``locales/*.po`` or ``i18n/*.json``)

4. Weblate will automatically detect:

   * Translation file format
   * Available languages
   * Source language

5. Review and confirm the detected settings

.. image:: /screenshots/user-add-component-discovery.webp

.. hint::

   For repositories with multiple translation components (e.g., separate files for
   backend, frontend, documentation), create a separate Weblate component for each.
   You can speed this up using :guilabel:`From existing component` for shared repositories.

.. seealso::

   * :ref:`component` for all configuration options
   * :ref:`bimono` for understanding monolingual vs. bilingual formats

Step 3: Invite and manage users
--------------------------------

Set up access control
+++++++++++++++++++++

Choose your project's visibility and access level:

1. Go to your project settings: :guilabel:`Operations` → :guilabel:`Settings` → :guilabel:`Access` tab
2. Select the appropriate :ref:`access control <acl>`:

   * **Public**: Open-source projects, anyone can contribute
   * **Protected**: Visible to all, but only invited users can translate
   * **Private**: Only invited users can view and translate

.. image:: /screenshots/project-access.webp

.. seealso::

   :ref:`manage-acl` for detailed access control configuration

Invite translators
++++++++++++++++++

For **Protected** and **Private** projects:

1. Navigate to :guilabel:`Operations` → :guilabel:`Users` in your project
2. Use :guilabel:`Add user` to invite translators
3. Assign them to appropriate teams:

   * **Translators**: Can translate strings
   * **Reviewers**: Can review and approve translations
   * **Managers**: Can manage project settings

For **Public** projects, users can start contributing immediately after signing up.

.. tip::

   Send your translators a welcome message with:

   * Link to your project on Weblate
   * Overview of any project-specific terminology or style guides
   * Information about your review process

.. seealso::

   * :ref:`manage-acl` for team management
   * :doc:`/admin/access` for advanced permission configuration

Step 4: Configure your workflow
--------------------------------

Set up continuous localization
+++++++++++++++++++++++++++++++

Enable automatic updates and commits:

1. Configure repository integration:

   * **Pull changes**: Set up a :ref:`webhook <update-vcs>` so Weblate updates when your source code changes
   * **Push changes**: Configure :ref:`push-changes` so translations are committed back to your repository

2. Enable automatic actions in component settings:

   * **Push on commit**: Automatically push translations to your repository
   * **Commit interval**: Set how often pending translations are committed (e.g., every 24 hours)

.. seealso::

   :ref:`continuous-translation` for complete workflow automation

Configure quality checks and workflows
+++++++++++++++++++++++++++++++++++++

Customize translation quality controls:

1. **Enable checks**: Review :ref:`checks` to ensure translation quality
2. **Set up review workflow**: Enable :ref:`project-translation_review` if you want approval process
3. **Add enforced checks**: Configure which quality checks should block translations

Optional: Enable add-ons
+++++++++++++++++++++++++

Weblate offers :ref:`addons` to automate common tasks:

* :ref:`addon-weblate.gettext.msgmerge`: Automatically update PO files from POT templates
* :ref:`addon-weblate.cleanup.generic`: Remove unused translation strings
* :ref:`addon-weblate.git.squash`: Squash commits before pushing to your repository
* :ref:`addon-weblate.discovery.discovery`: Automatically discover new translation files

.. seealso::

   :doc:`/admin/addons` for all available add-ons

Step 5: Test and verify
------------------------

Before announcing the migration to your translators:

1. **Test the workflow**:

   * Make a test translation
   * Verify it appears in your Git repository
   * Test pulling changes from your repository into Weblate

2. **Import any existing translation memory** (optional):

   * Use :ref:`translation-memory` to import previous translations
   * This helps with consistency and speeds up translation

3. **Configure notifications**:

   * Set up :ref:`notifications` for translation events
   * Configure repository :ref:`hooks` for your Git hosting service

.. seealso::

   :doc:`/admin/memory` for translation memory management

Next steps
----------

After completing the migration:

* **Announce to translators**: Let your translation team know about the migration with clear instructions
* **Monitor initial usage**: Watch for any issues during the first few days
* **Gather feedback**: Ask translators about their experience compared to the previous platform
* **Optimize workflow**: Adjust settings based on your team's needs

Additional resources
--------------------

* :doc:`integration` - Detailed integration patterns
* :doc:`/workflows` - Different workflow configurations
* :doc:`/admin/continuous` - Automated continuous localization
* :doc:`/api` - API for automation and integrations
* :doc:`/devel/reporting` - Setting up translation progress reports
* :ref:`faq` - Frequently asked questions

.. hint::

   Join the `Weblate community <https://weblate.org/support/>`_ if you need help
   during your migration. The community is active and helpful!

Common migration scenarios
--------------------------

Migrating from Transifex
+++++++++++++++++++++++++

* **File format**: Transifex often uses PO files - these work directly with Weblate
* **Git integration**: If using Transifex GitHub integration, you can point Weblate to the same repository
* **Translation memory**: Export from Transifex and import into Weblate's :ref:`translation-memory`

Migrating from Crowdin
+++++++++++++++++++++++

* **File format**: Export in your native format (not Crowdin-specific format)
* **Branch workflow**: Crowdin's branch-per-language can be replaced with Weblate's VCS integration
* **Screenshots**: Weblate supports :ref:`screenshots` for translation context

Migrating from Lokalise
++++++++++++++++++++++++

* **File format**: Export all languages in your original format
* **Key management**: For key-based formats (JSON, YAML), ensure keys match your codebase
* **Quality checks**: Review Lokalise's QA rules and configure equivalent :ref:`checks` in Weblate

.. tip::

   During migration, you can run both platforms in parallel for a transition period
   to ensure everything works as expected before fully switching over.
