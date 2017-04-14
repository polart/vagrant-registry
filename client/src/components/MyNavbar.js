import React, {Component} from "react";
import {Nav, Navbar, NavItem} from "react-bootstrap";
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

  render() {
    return (
        <Navbar fixedTop inverse collapseOnSelect>
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
          </Navbar.Collapse>
        </Navbar>
    );
  }
}
