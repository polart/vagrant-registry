import React, {Component} from "react";
import {FormGroup, Radio} from "react-bootstrap";


export default class BoxOrdering extends Component {
  onBoxOrderChange = (e) => {
    const location = this.props.router.createLocation({
      pathname: this.location.pathname,
      query: Object.assign({}, this.location.query, {
        order: e.target.value,
      }),
    });
    this.props.router.push(location);
  };

  render() {
    this.location = this.props.router.location;
    const order = this.location.query.order || 'pulls';
    return (
        <FormGroup>
          <label>Order by:</label>{' '}
          <Radio name="boxOrder"
                 value="pulls"
                 checked={order === 'pulls'}
                 inline
                 onChange={this.onBoxOrderChange}
          >
            Downloads
          </Radio>
          {' '}
          <Radio name="boxOrder"
                 value="updated"
                 checked={order === 'updated'}
                 inline
                 onChange={this.onBoxOrderChange}
          >
            Last updated
          </Radio>
        </FormGroup>
    );
  }
}
