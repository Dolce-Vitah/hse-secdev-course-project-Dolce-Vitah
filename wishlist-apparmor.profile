#include <tunables/global>

/usr/bin/uvicorn {
  include <abstractions/base>
  include <abstractions/python>
  include <abstractions/nameservice>
  include <abstractions/ssl_certs>
  include <abstractions/user-tmp>

  network inet stream,
  network inet6 stream,
  network inet dgram,
  network inet6 dgram,
  capability net_bind_service,

  /app/** r,
  /tmp/** rw,

  /usr/lib/** r,
  /usr/lib/python3.11/** r,
  /usr/local/lib/** r,
  /usr/local/lib/python3.11/** r,
  /usr/local/bin/** rix,

  /etc/ssl/** r,
  /etc/pki/** r,

  /usr/share/zoneinfo/** r,
  /usr/share/locale/** r,

  deny /** w,
  deny /** rwklx,

  /usr/bin/uvicorn rix,
  /usr/bin/python3.11 rix,
  /usr/bin/python3 rix,

  /usr/lib/libpq.so.* r,
  /usr/local/lib/libpq.so.* r,

  /proc/** r,
  deny /proc/sys/** rwk,

  deny capability sys_ptrace,
  deny capability setuid,
  deny capability setgid,
  deny capability sys_module,

  /etc/resolv.conf r,
  /etc/hosts r,
  /etc/nsswitch.conf r,

  deny network raw,
  deny @{HOME}/** rw,

}
