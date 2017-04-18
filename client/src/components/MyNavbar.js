import React, {Component} from "react";
import {MenuItem, Nav, Navbar, NavDropdown, NavItem} from "react-bootstrap";
import {Link} from "react-router";
import NavSearchForm from "./NavSearchForm";


export default class MyNavbar extends Component {
  onNavSelect = (key) => {
    if (key === 'boxes') {
      this.props.router.replace({
        pathname: '/boxes/',
      })
    }
  };

  onAccountClick = (e) => {
    e.preventDefault();
    this.props.router.push('/account/');
  };

  onLogoutClick = (e) => {
    e.preventDefault();
    this.props.onLogout();
  };

  onLoginClick = (e) => {
    e.preventDefault();
    this.props.router.push('/login/');
  };

  renderUser = () => {
    if (!this.props.username) {
      return <NavItem href="/login/" onClick={this.onLoginClick}>Sign In</NavItem>;
    }

    return (
      <NavDropdown eventKey={3} title={this.props.username} id="navUserAccount">
        <MenuItem onClick={this.onAccountClick} href="/account/">Account</MenuItem>
        {this.props.isStaff && <MenuItem href="/admin/">Admin</MenuItem>}
        <MenuItem divider />
        <MenuItem onClick={this.onLogoutClick}>Logout</MenuItem>
      </NavDropdown>
    )
  };

  render() {
    return (
        <Navbar inverse collapseOnSelect>
          <Navbar.Header>
            <Navbar.Brand>
              <Link to='/'>Vagrant Registry</Link>
            </Navbar.Brand>
            <Navbar.Toggle />
          </Navbar.Header>

          <Navbar.Collapse>
            <Nav onSelect={this.onNavSelect}>
              <NavItem eventKey="boxes" href="/boxes/" >Boxes</NavItem>
            </Nav>
            <NavSearchForm router={this.props.router} />

            <Nav pullRight>
              {this.renderUser()}
            </Nav>
          </Navbar.Collapse>
        </Navbar>
    );
  }
}
