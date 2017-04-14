import React, {Component} from "react";
import {Button, FormControl, FormGroup, Glyphicon, InputGroup, Navbar} from "react-bootstrap";


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
                  value={this.state.searchValue}
                  onChange={this.onSearchChange}
                  onKeyPress={this.onSearchKeyPress}
              />
              <InputGroup.Button>
                <Button onClick={this.onSearch}>
                  <Glyphicon glyph="search" />
                </Button>
              </InputGroup.Button>
            </InputGroup>
          </FormGroup>
        </Navbar.Form>
    );
  }
}
