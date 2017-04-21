import React, {Component} from "react";
import {Button, FormControl, FormGroup, Glyphicon, InputGroup, Navbar} from "react-bootstrap";

import '../styles/NavSearchForm.css';


export default class NavSearchForm extends Component {
  state = {
    searchValue: this.props.router.location.query.q || '',
  };

  onSearchChange = (e) => {
    this.setState({searchValue: e.target.value});
  };

  onSearchKeyPress = (e) => {
    if (e.key === 'Enter') {
      this.onSearch();
    }
  };

  onSearch = () => {
    if (!this.state.searchValue.length) {
      return;
    }
    const location = this.props.router.createLocation({
      pathname: '/boxes/search/',
      query: {
        q: this.state.searchValue,
      }
    });
    this.props.router.push(location);
  };

  render() {
    return (
        <Navbar.Form pullLeft>
          <FormGroup>
            <InputGroup>
              <FormControl
                  type="text"
                  placeholder="Search"
                  className="search-input"
                  value={this.state.searchValue}
                  onChange={this.onSearchChange}
                  onKeyPress={this.onSearchKeyPress}
              />
              <InputGroup.Button>
                <Button className="search-button" onClick={this.onSearch}>
                  <Glyphicon glyph="search" />
                </Button>
              </InputGroup.Button>
            </InputGroup>
          </FormGroup>
        </Navbar.Form>
    );
  }
}
