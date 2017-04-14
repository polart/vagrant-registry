import React, {Component} from "react";
import {Pagination} from "react-bootstrap";


export default class MyPagination extends Component {
  onPageChange = (page) => {
    const location = this.props.router.createLocation({
      pathname: this.location.pathname,
      query: Object.assign({}, this.location.query, { page }),
    });
    this.props.router.push(location);
  };

  render() {
    this.location = this.props.router.location;
    this.activePage = parseInt(this.location.query.page || 1, 10);
    this.perPage = this.props.perPage || 10;

    if (this.props.itemsCount <= this.perPage) {
      return null;
    }

    const items = Math.ceil(this.props.itemsCount / this.perPage);
    return (
        <Pagination
            prev
            next
            first
            last
            ellipsis
            boundaryLinks
            items={items}
            maxButtons={5}
            activePage={this.activePage}
            onSelect={this.onPageChange}
        />
    );
  }
}
