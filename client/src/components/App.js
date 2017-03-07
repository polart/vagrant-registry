import React, { Component } from 'react';
import { Navbar, Nav, NavItem } from 'react-bootstrap';
import { Link } from 'react-router';


class App extends Component {
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
                <Link to='/'>Vagrant Registry</Link>
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
