# for a pre-release, define the prerel field e.g. .a1 .rc2 - comment out for official release
# also remove the space between % and global - this space is needed because
# fedpkg verrel stupidly ignores comment lines
%global prerel .b3
# also need the relprefix field for a pre-release e.g. .0 - also comment out for official release
%global relprefix 0.

Name:             pki-ra
Version:          10.0.0
Release:          %{?relprefix}11%{?prerel}%{?dist}
Summary:          Certificate System - Registration Authority
URL:              http://pki.fedoraproject.org/
License:          GPLv2
Group:            System Environment/Daemons

BuildArch:        noarch

BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# specify '_unitdir' macro for platforms that don't use 'systemd'
%if 0%{?rhel} || 0%{?fedora} < 16
%define           _unitdir /lib/systemd/system
%endif

BuildRequires:    cmake
BuildRequires:    nspr-devel
BuildRequires:    nss-devel

Requires:         mod_nss >= 1.0.8
Requires:         mod_perl >= 1.99_16
Requires:         mod_revocator >= 1.0.3
Requires:         pki-server >= 10.0.0
Requires:         pki-ra-theme >= 10.0.0
Requires:         perl-DBD-SQLite
Requires:         sqlite
Requires:         /usr/sbin/sendmail
%if 0%{?fedora} >= 16
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
%else
Requires(post):   chkconfig
Requires(preun):  chkconfig
Requires(preun):  initscripts
Requires(postun): initscripts
Requires:         initscripts
%endif

Source0:          http://pki.fedoraproject.org/pki/sources/%{name}/%{name}-%{version}%{?prerel}.tar.gz

%description
Certificate System (CS) is an enterprise software system designed
to manage enterprise Public Key Infrastructure (PKI) deployments.

The Registration Authority (RA) is an optional PKI subsystem that acts as a
front-end for authenticating and processing enrollment requests, PIN reset
requests, and formatting requests.

An RA communicates over SSL with a Certificate Authority (CA) to fulfill
the user's requests. An RA may often be located outside an organization's
firewall to allow external users the ability to communicate with that
organization's PKI deployment.

For deployment purposes, an RA requires the following components from the PKI
Core package:

  * pki-server
  * pki-tools
  * pki-selinux (f17 only)

Additionally, Certificate System requires ONE AND ONLY ONE of the following
"Mutually-Exclusive" PKI Theme packages:

  * dogtag-pki-theme (Dogtag Certificate System deployments)
  * redhat-pki-theme (Red Hat Certificate System deployments)


%prep


%setup -q -n %{name}-%{version}%{?prerel}

cat << \EOF > %{name}-prov
#!/bin/sh
%{__perl_provides} $* |\
sed -e '/perl(PKI.*)/d' -e '/perl(Template.*)/d'
EOF

%global __perl_provides %{_builddir}/%{name}-%{version}%{?prerel}/%{name}-prov
chmod +x %{__perl_provides}

cat << \EOF > %{name}-req
#!/bin/sh
%{__perl_requires} $* |\
sed -e '/perl(PKI.*)/d' -e '/perl(Template.*)/d'
EOF

%global __perl_requires %{_builddir}/%{name}-%{version}%{?prerel}/%{name}-req
chmod +x %{__perl_requires}


%clean
%{__rm} -rf %{buildroot}


%build
%{__mkdir_p} build
cd build
%cmake -DVERSION=%{version}-%{release} \
	-DVAR_INSTALL_DIR:PATH=/var \
	-DBUILD_PKI_RA:BOOL=ON \
	-DSYSTEMD_LIB_INSTALL_DIR=%{_unitdir} \
	..
%{__make} VERBOSE=1 %{?_smp_mflags}


%install
%{__rm} -rf %{buildroot}
cd build
%{__make} install DESTDIR=%{buildroot} INSTALL="install -p"

chmod 755 %{buildroot}%{_datadir}/pki/ra/docroot/*.cgi
chmod 755 %{buildroot}%{_datadir}/pki/ra/docroot/admin/*.cgi
chmod 755 %{buildroot}%{_datadir}/pki/ra/docroot/admin/group/*.cgi
chmod 755 %{buildroot}%{_datadir}/pki/ra/docroot/admin/user/*.cgi
chmod 755 %{buildroot}%{_datadir}/pki/ra/docroot/agent/*.cgi
chmod 755 %{buildroot}%{_datadir}/pki/ra/docroot/agent/cert/*.cgi
chmod 755 %{buildroot}%{_datadir}/pki/ra/docroot/agent/request/*.cgi
chmod 755 %{buildroot}%{_datadir}/pki/ra/docroot/ee/*.cgi
chmod 755 %{buildroot}%{_datadir}/pki/ra/docroot/ee/agent/*.cgi
chmod 755 %{buildroot}%{_datadir}/pki/ra/docroot/ee/request/*.cgi
chmod 755 %{buildroot}%{_datadir}/pki/ra/docroot/ee/scep/*.cgi
chmod 755 %{buildroot}%{_datadir}/pki/ra/docroot/ee/server/*.cgi
chmod 755 %{buildroot}%{_datadir}/pki/ra/docroot/ee/user/*.cgi

%if 0%{?fedora} >= 15
# Details:
#
#     * https://fedoraproject.org/wiki/Features/var-run-tmpfs
#     * https://fedoraproject.org/wiki/Tmpfiles.d_packaging_draft
#
%{__mkdir_p} %{buildroot}%{_sysconfdir}/tmpfiles.d
# generate 'pki-ra.conf' under the 'tmpfiles.d' directory
echo "D /var/lock/pki 0755 root root -"    >  %{buildroot}%{_sysconfdir}/tmpfiles.d/pki-ra.conf
echo "D /var/lock/pki/ra 0755 root root -" >> %{buildroot}%{_sysconfdir}/tmpfiles.d/pki-ra.conf
echo "D /var/run/pki 0755 root root -"     >> %{buildroot}%{_sysconfdir}/tmpfiles.d/pki-ra.conf
echo "D /var/run/pki/ra 0755 root root -"  >> %{buildroot}%{_sysconfdir}/tmpfiles.d/pki-ra.conf
%endif

%if 0%{?fedora} >= 16
%{__rm} %{buildroot}%{_initrddir}/pki-rad
%else
%{__rm} -rf %{buildroot}%{_sysconfdir}/systemd/system/pki-rad.target.wants
%{__rm} -rf %{buildroot}%{_unitdir}
%endif

%if 0%{?rhel} || 0%{?fedora} < 16
%post
# This adds the proper /etc/rc*.d links for the script
/sbin/chkconfig --add pki-rad || :


%preun
if [ $1 = 0 ] ; then
    /sbin/service pki-rad stop >/dev/null 2>&1
    /sbin/chkconfig --del pki-rad || :
fi


%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service pki-rad condrestart >/dev/null 2>&1 || :
fi

%else
%post
# Attempt to update ALL old "RA" instances to "systemd"
if [ -d /etc/sysconfig/pki/ra ]; then
    for inst in `ls /etc/sysconfig/pki/ra`; do
        if [ ! -e "/etc/systemd/system/pki-rad.target.wants/pki-rad@${inst}.service" ]; then
            ln -s "/lib/systemd/system/pki-rad@.service" \
                  "/etc/systemd/system/pki-rad.target.wants/pki-rad@${inst}.service"

            if [ -e /var/run/${inst}.pid ]; then
                kill -9 `cat /var/run/${inst}.pid` || :
                rm -f /var/run/${inst}.pid
                echo "pkicreate.systemd.servicename=pki-rad@${inst}.service" >> \
                     /var/lib/${inst}/conf/CS.cfg || :
                /bin/systemctl daemon-reload >/dev/null 2>&1 || :
                /bin/systemctl restart pki-rad@${inst}.service || :
            else
                echo "pkicreate.systemd.servicename=pki-rad@${inst}.service" >> \
                     /var/lib/${inst}/conf/CS.cfg || :
            fi
        else
            # Conditionally restart this Dogtag 9 instance
            /bin/systemctl condrestart pki-rad@${inst}.service
        fi
    done
fi
/bin/systemctl daemon-reload >/dev/null 2>&1 || :

%preun
if [ $1 = 0 ] ; then
    /bin/systemctl --no-reload disable pki-rad.target > /dev/null 2>&1 || :
    /bin/systemctl stop pki-rad.target > /dev/null 2>&1 || :
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ "$1" -ge "1" ] ; then
    /bin/systemctl try-restart pki-rad.target >/dev/null 2>&1 || :
fi
%endif


%files
%defattr(-,root,root,-)
%doc base/ra/LICENSE
%if 0%{?fedora} >= 16
%dir %{_sysconfdir}/systemd/system/pki-rad.target.wants
%{_unitdir}/pki-rad@.service
%{_unitdir}/pki-rad.target
%else
%{_initrddir}/pki-rad
%endif
%dir %{_datadir}/pki/ra
%{_datadir}/pki/ra/conf/
%{_datadir}/pki/ra/docroot/
%{_datadir}/pki/ra/lib/
%{_datadir}/pki/ra/scripts/
%{_datadir}/pki/ra/setup/
%dir %{_localstatedir}/lock/pki/ra
%dir %{_localstatedir}/run/pki/ra
%if 0%{?fedora} >= 15
# Details:
#
#     * https://fedoraproject.org/wiki/Features/var-run-tmpfs
#     * https://fedoraproject.org/wiki/Tmpfiles.d_packaging_draft
#
%config(noreplace) %{_sysconfdir}/tmpfiles.d/pki-ra.conf
%endif


%changelog
* Mon Nov 12 2012 Ade Lee <alee@redhat.com> 10.0.0-0.11.b3
- Update release to b3

* Mon Oct 29 2012 Ade Lee <alee@redhat.com> 10.0.0-0.10.b2
- Update release to b2

* Mon Oct 8 2012 Ade Lee <alee@redhat.com> 10.0.0-0.9.b1
- Update release to b1

* Fri Oct 5 2012 Endi S. Dewata <edewata@redhat.com> 10.0.0-0.9.a2
- Merged pki-silent into pki-server.

* Mon Oct 1 2012 Ade Lee <alee@redhat.com> 10.0.0-0.8.a2
- Update release to a2

* Sun Sep 30 2012 Endi S. Dewata <edewata@redhat.com> 10.0.0-0.8.a1
- Modified CMake to use RPM version number

* Mon Sep 24 2012 Endi S. Dewata <edewata@redhat.com> 10.0.0-0.7.a1
- Merged pki-setup into pki-server

* Tue Sep 11 2012 Matthew Harmsen <mharmsen@redhat.com> 10.0.0-0.6.a1
- TRAC Ticket #312 - Dogtag 10: Automatically restart any running instances
  upon RPM "update" . . .

* Mon Aug 20 2012 Endi S. Dewata <edewata@redhat.com> 10.0.0-0.5.a1
- Removed direct dependency on 'pki-native-tools'.

* Mon Aug 20 2012 Endi S. Dewata <edewata@redhat.com> 10.0.0-0.4.a1
- Replaced 'pki-deploy' with 'pki-server'.

* Thu Aug 16 2012 Matthew Harmsen <mharmsen@redhat.com> 10.0.0-0.3.a1
- Added 'pki-deploy' runtime dependency

* Mon Aug 13 2012 Ade Lee <alee@redhat.com> 10.0.0-0.2.a1
- Added systemd scripts
- Ported config files and init scripts to apache 2.4

* Wed Feb  1 2012 Nathan Kinder <nkinder@redhat.com> 10.0.0-0.1.a1
- Updated package version number

* Thu Sep 22 2011 Ade Lee <alee@redhat.com> 9.0.4-1
- Bugzilla Bug #733065 - User enrollment with RA -- this fails with
  CA Connection Error

* Thu Jul 14 2011 Matthew Harmsen <mharmsen@redhat.com> 9.0.3-1
- Bugzilla Bug #694569 - parameter used by pkiremove not updated (alee)
- Bugzilla Bug #699364 - PKI-RA instance not created successfully (alee)
- Bugzilla Bug #699837 - service command is not fully backwards
  compatible with Dogtag pki subsystems (mharmsen)
- Bugzilla Bug #717765 - TPS configuration: logging into security domain
  from tps does not work with clientauth=want. (alee)
- Bugzilla Bug #669226 - Remove Legacy Build System (mharmsen)

* Tue Apr 26 2011 Matthew Harmsen <mharmsen@redhat.com> 9.0.2-1
- Bugzilla Bug #694569 - parameter used by pkiremove not updated
- Bugzilla Bug #699364 - PKI-RA instance not created successfully
- Bugzilla Bug #699837 - service command is not fully backwards compatible
  with Dogtag pki subsystems

* Fri Mar 25 2011 Matthew Harmsen <mharmsen@redhat.com> 9.0.1-1
- Bugzilla Bug #690950 - Update Dogtag Packages for Fedora 15 (beta)
- Bugzilla Bug #684381 - CS.cfg specifies incorrect type of comments

* Wed Dec 1 2010 Matthew Harmsen <mharmsen@redhat.com> 9.0.0-1
- Updated Dogtag 1.3.x --> Dogtag 2.0.0 --> Dogtag 9.0.0
- Bugzilla Bug #620925 - CC: auditor needs to be able to download audit logs
  in the java subsystems
- Bugzilla Bug #651916 - kra and ocsp are using incorrect ports
  to talk to CA and complete configuration in DonePanel
- Bugzilla Bug #632425 - Port to tomcat6
- Bugzilla Bug #638377 - Generate PKI UI components which exclude
  a GUI interface
- Bugzilla Bug #643206 - New CMake based build system for Dogtag
- Bugzilla Bug #499494 - change CA defaults to SHA2
- Bugzilla Bug #656664 - Please Update Spec File to use 'ghost' on files
  in /var/run and /var/lock
- Bugzilla Bug #606943 - Convert RA to use ldap utilities from
  OpenLDAP instead of the Mozldap

* Thu Apr 08 2010 Matthew Harmsen <mharmsen@redhat.com> 1.3.1-1
- Bugzilla Bug #564131 - Config wizard : all subsystems - done panel text
  needs correction

* Tue Feb 16 2010 Matthew Harmsen <mharmsen@redhat.com> 1.3.0-6
- Bugzilla Bug #566060 - Add 'pki-native-tools' as a runtime dependency
  for RA, and TPS . . .

* Fri Jan 29 2010 Matthew Harmsen <mharmsen@redhat.com> 1.3.0-5
- Bugzilla Bug #553076 - Apply "registry" logic to pki-ra . . .
- Applied filters for unwanted perl provides and requires
- Restored "perl-DBD-SQLite" runtime dependency

* Tue Jan 26 2010 Matthew Harmsen <mharmsen@redhat.com> 1.3.0-4
- Bugzilla Bug #553850 - Review Request: pki-ra - Dogtag Registration Authority
- Per direction from the Fedora community,
  removed the following explicit "Requires":
      perl-DBI
      perl-HTML-Parser
      perl-HTML-Tagset
      perl-Parse-RecDescent
      perl-URI
      perl-XML-NamespaceSupport
      perl-XML-Parser
      perl-XML-Simple

* Thu Jan 14 2010 Matthew Harmsen <mharmsen@redhat.com> 1.3.0-3
- Bugzilla Bug #512234 - Move pkiuser:pkiuser check from spec file into pkicreate . . .
- Bugzilla Bug #547471 - Apply PKI SELinux changes to PKI registry model
- Bugzilla Bug #553076 - Apply "registry" logic to pki-ra . . .
- Bugzilla Bug #553078 - Apply "registry" logic to pki-tps . . .
- Bugzilla Bug #553850 - Review Request: pki-ra - Dogtag Registration Authority

* Mon Dec 14 2009 Kevin Wright <kwright@redhat.com> 1.3.0-2
- Removed 'with exceptions' from License

* Fri Oct 16 2009 Ade Lee <alee@redhat.com> 1.3.0-1
- Bugzilla Bug #X - Fedora Packaging Changes

