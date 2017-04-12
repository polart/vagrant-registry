import React, { Component } from 'react';
import {Navbar, Nav, NavItem, FormGroup, FormControl, Button, InputGroup, Glyphicon} from 'react-bootstrap';
import { Link } from 'react-router';
import * as auth from "../auth";


class App extends Component {
  state = {
    searchValue: this.props.location.query.q || '',
  };

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

  onSearch = () => {
    const location = this.props.router.createLocation({
      pathname: '/boxes/search/',
      query: {
        q: this.state.searchValue,
      }
    });
    this.props.router.push(location);
  };

  onSearchChange = (e) => {
    this.setState({searchValue: e.target.value});
  };

  onSearchKeyPress = (e) => {
    if (e.key === 'Enter') {
      this.onSearch();
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

              <Navbar.Form pullLeft>
                <FormGroup>
                  <InputGroup>
                    <FormControl
                        type="text"
                        placeholder="Search"
                        value={this.state.searchValue}
                        onChange={this.onSearchChange}
                        onKeyPress={this.onSearchKeyPress}
                    />
                    <InputGroup.Button>
                      <Button onClick={this.onSearch}><Glyphicon glyph="search" /></Button>
                    </InputGroup.Button>
                  </InputGroup>
                </FormGroup>
              </Navbar.Form>
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
