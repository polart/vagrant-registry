import React, {Component} from "react";
import { connect } from 'react-redux';
import {ListGroup, ListGroupItem, Label, Pagination} from 'react-bootstrap';
import Moment from 'moment';
import * as actions from "../actions";
import MySpinner from "./MySpinner";


class BoxVersionList extends Component {
  state = {
    page: 1,
  };

  componentDidMount() {
    this.props.fetchBoxVersions(this.props.boxTag, this.state.page);
  }

  onPageChange = (page) => {
    this.props.fetchBoxVersions(this.props.boxTag, page);
    this.setState({page});
  };

  onBoxVersionClick = (e) => {
    e.preventDefault();
    this.props.router.push(
        // Relative url
        e.currentTarget.getAttribute("href")
    );
    return false;
  };

  renderPagination = () => {
    if (this.pages.count <= 10) {
      return null;
    }

    const items = Math.ceil(this.pages.count / 10);
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
            activePage={this.state.page}
            onSelect={this.onPageChange}
        />
    );
  };

  renderProviders = (version) => {
    return version.providers.map((providerTag) => {
      const provider = this.props.boxProviders[providerTag];
      return (
          <span key={providerTag} >
            <Label bsStyle="primary">
              {provider.provider}
            </Label>
            &nbsp;
          </span>
      );
    });
  };

  renderVersionsList = () => {
    return this.versionTags.map(tag => {
      const version = this.props.boxVersions[tag];
      return (
          <ListGroupItem
              key={version.version}
              href={`/boxes/${this.props.boxTag}/versions/${version.version}/`}
              onClick={this.onBoxVersionClick}
          >
            <h4 className="list-group-item-heading">
              v{version.version} |&nbsp;
              <small title={Moment(version.date_updated).format('LLL')}>
                Last updated: {Moment(version.date_updated).fromNow()}
              </small>
            </h4>
            <p>{version.changes}</p>
            {this.renderProviders(version)}
          </ListGroupItem>
      );
    });
  };

  render() {
    this.pages = this.props.boxVersionsPages;
    this.versionTags = (this.pages && this.pages.pages[this.state.page]) || [];

    if (!this.pages || !this.versionTags.length) {
      return <MySpinner />;
    }

    if (this.pages.count === 0) {
      return <p>No versions</p>
    }

    return (
        <div>
          <ListGroup>
            {this.renderVersionsList()}
          </ListGroup>
          {this.renderPagination()}
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  return {
    boxVersions: state.entities.boxVersions,
    boxVersionsPages: state.pagination.boxVersions[props.boxTag],
    boxProviders: state.entities.boxProviders,
  };
}

export default connect(mapStateToProps, {
  fetchBoxVersions: actions.loadBoxVersions,
})(BoxVersionList)
