var Navbar = ReactBootstrap.Navbar;
var Nav = ReactBootstrap.Nav;

function MyNavbar (props) {
  return (
    <Navbar bg={props.color} variant={props.variant} fixed="top" expand="sm">
      <Navbar.Brand href={props.brandhref}>{props.brandlabel}</Navbar.Brand>
      <Navbar.Toggle/>
      <Navbar.Collapse>
      <Nav className="ml-auto">
        {props.navs.map((nav) => (
          <Nav.Link href={nav.href}>{nav.label}</Nav.Link>
        ))}
      </Nav>
      </Navbar.Collapse>
    </Navbar>
  );
};

// MyNavbarをグローバルスコープにエクスポート
window.MyNavbar = MyNavbar;