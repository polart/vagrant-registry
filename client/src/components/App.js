import React, { Component } from 'react';
import { Navbar, Nav, NavItem } from 'react-bootstrap';
import { Link } from 'react-router';
import * as auth from "../auth";


class App extends Component {
  componentWillMount() {
    this.checkLogin();
  }

  checkLogin = () => {
    const requireLogin = () => {
      this.props.router.push(
          `/login/?next=${this.props.router.location.pathname}`
      );
    };

    if (auth.loggedIn()) {
      auth.tokenValid()
          .then(() => {
            if (this.props.router.location.pathname === '/') {
              this.props.router.push('/boxes/me/');
            }
          })
          .catch(requireLogin);
    } else {
      requireLogin();
    }
  };

  onNavSelect = (key) => {
    if (key === 'boxes') {
      this.props.router.replace({
        pathname: '/boxes/',
      })
    }
  };

  render() {
    return (
        <div>
          <Navbar fixedTop inverse collapseOnSelect>
            <Navbar.Header>
              <Navbar.Brand>
                <Link to='/boxes/'>Vagrant Registry</Link>
              </Navbar.Brand>
              <Navbar.Toggle />
            </Navbar.Header>
            <Navbar.Collapse>
              <Nav onSelect={this.onNavSelect}>
                <NavItem eventKey="boxes" href="/boxes/" >Boxes</NavItem>
              </Nav>
            </Navbar.Collapse>
          </Navbar>

          <div style={{marginTop: '60px'}}>
            {this.props.children}
          </div>
        </div>
    );
  }
}

export default App;
